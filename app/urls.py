from django.urls import path
from .views import UploadCSVView, DatasetListView, DatasetDetailView, MatplotlibChartView, PDFReportView

urlpatterns = [
    path('upload/', UploadCSVView.as_view(), name='upload-csv'),
    path('datasets/', DatasetListView.as_view(), name='datasets-list'),
    path('datasets/<uuid:pk>/', DatasetDetailView.as_view(), name='dataset-detail'),
    path('datasets/<uuid:pk>/chart-matplotlib/', MatplotlibChartView.as_view(), name='chart-matplotlib'),
    path('datasets/<uuid:pk>/report-pdf/', PDFReportView.as_view(), name='report-pdf'),
]
