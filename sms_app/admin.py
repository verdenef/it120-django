from django.contrib import admin
from .models import SMSLog


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    """
    Admin configuration for the SMSLog model.
    """
    list_display = ('recipient', 'status', 'gateway_message_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('recipient', 'message', 'gateway_message_id')
    readonly_fields = ('created_at',)
