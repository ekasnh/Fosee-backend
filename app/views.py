import io
import pandas as pd
from django.http import FileResponse, HttpResponse
from django.views import View
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Dataset
from .serializers import DatasetSerializer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class UploadCSVView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'detail':'No file provided'}, status=400)
        try:
            df = pd.read_csv(file_obj)
        except Exception as e:
            return Response({'detail': f'Error reading CSV: {str(e)}'}, status=400)

        count = len(df)
        numeric_cols = ['Flowrate', 'Pressure', 'Temperature']
        averages = {c: (float(df[c].dropna().mean()) if c in df.columns else None) for c in numeric_cols}
        type_dist = df['Type'].value_counts(dropna=True).to_dict() if 'Type' in df.columns else {}
        summary = {
            'total_count': count,
            'averages': averages,
            'type_distribution': type_dist
        }

        dataset = Dataset.objects.create(
            name=file_obj.name,
            csv_file=file_obj,
            raw_csv_text=df.to_csv(index=False),
            summary=summary,
            row_count=count,
            sample_rows=df.head(10).to_dict(orient='records')
        )

        # prune older datasets, keep last 5
        qs = Dataset.objects.order_by('-uploaded_at')
        ids_to_keep = [d.id for d in qs[:5]]
        Dataset.objects.exclude(id__in=ids_to_keep).delete()

        serializer = DatasetSerializer(dataset)
        return Response(serializer.data, status=201)

class DatasetListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DatasetSerializer

    def get_queryset(self):
        return Dataset.objects.all()[:5]

class DatasetDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DatasetSerializer
    queryset = Dataset.objects.all()

class MatplotlibChartView(View):
    def get(self, request, pk):
        try:
            dataset = Dataset.objects.get(pk=pk)
        except Dataset.DoesNotExist:
            return HttpResponse(status=404)
        df = pd.read_csv(dataset.csv_file.path)
        if 'Type' in df.columns:
            counts = df['Type'].value_counts()
        else:
            counts = pd.Series()
        fig, ax = plt.subplots(figsize=(6,4))
        counts.plot(kind='bar', ax=ax)
        ax.set_title('Equipment Type Distribution')
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return HttpResponse(buf.getvalue(), content_type='image/png')

class PDFReportView(View):
    def get(self, request, pk):
        try:
            dataset = Dataset.objects.get(pk=pk)
        except Dataset.DoesNotExist:
            return HttpResponse(status=404)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        text = p.beginText(40, 800)
        text.setFont("Helvetica", 12)
        text.textLine(f"Dataset: {dataset.name}")
        text.textLine(f"Uploaded at: {dataset.uploaded_at.isoformat()}")
        text.textLine(" ")
        summary = dataset.summary
        text.textLine(f"Total equipments: {summary.get('total_count')}")
        text.textLine("Averages:")
        for k, v in summary.get('averages', {}).items():
            text.textLine(f"  {k}: {v}")
        text.textLine(" ")
        text.textLine("Equipment type distribution:")
        for k, v in summary.get('type_distribution', {}).items():
            text.textLine(f"  {k}: {v}")
        p.drawText(text)
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"{dataset.name}-report.pdf")
