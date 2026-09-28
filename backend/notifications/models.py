from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        TRANSFER_COMPLETED = 'transfer_completed', 'Transfer completed'
        TRANSFER_FAILED = 'transfer_failed', 'Transfer failed'
        TRANSFER_RECEIVED = 'transfer_received', 'Transfer received'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    transaction = models.ForeignKey(
        'core.Transaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
    )
    kind = models.CharField(max_length=32, choices=Kind.choices)
    message = models.CharField(max_length=240)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.kind} for {self.recipient}'