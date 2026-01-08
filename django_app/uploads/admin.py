from django.contrib import admin
from .models import UserTargetUpload, DbtRunLog

admin.site.register(UserTargetUpload)

@admin.register(DbtRunLog)
class DbtRunLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'started_at', 'completed_at', 'duration_seconds', 'triggered_by']
    list_filter = ['status', 'triggered_by', 'started_at']
    readonly_fields = ['started_at', 'completed_at', 'duration_seconds']
    search_fields = ['output', 'error']
