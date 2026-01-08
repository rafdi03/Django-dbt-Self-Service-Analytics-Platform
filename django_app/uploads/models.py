from django.db import models

class UserTargetUpload(models.Model):
    month = models.DateField()
    target_amount = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'raw_user_targets'


class DbtRunLog(models.Model):
    """Model untuk menyimpan log dbt run"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    output = models.TextField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    triggered_by = models.CharField(max_length=100, default='upload')  # 'upload' or 'rerun'
    
    class Meta:
        db_table = 'dbt_run_logs'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"DBT Run {self.id} - {self.status} - {self.started_at}"
