import uuid
from django.db import models

class Dataset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to='uploads/')
    raw_csv_text = models.TextField(blank=True, null=True)
    summary = models.JSONField()
    row_count = models.IntegerField()
    sample_rows = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.name} ({self.row_count} rows)"
