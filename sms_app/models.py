from django.db import models


class SMSLog(models.Model):
    """
    Persists an audit record of an SMS dispatch attempt via the Textbee gateway.
    """
    STATUS_CHOICES = [
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]

    recipient = models.CharField(max_length=20, help_text="Recipient phone number")
    message = models.TextField(help_text="SMS message body")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='SENT',
        help_text="Dispatch outcome status",
    )
    gateway_message_id = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Textbee message or batch ID returned by gateway",
    )
    error_message = models.TextField(
        blank=True,
        default='',
        help_text="Error message or reason if dispatch failed",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when message dispatch attempt was recorded",
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'

    def __str__(self):
        created_str = self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else 'Unsaved'
        return f"[{self.status}] {self.recipient} ({created_str})"
