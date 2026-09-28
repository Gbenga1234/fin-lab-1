from django.conf import settings
from django.db import models


class Transaction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    reference = models.CharField(max_length=64, unique=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        null=True,
        blank=True,
    )
    source_account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.PROTECT,
        related_name='outgoing_transactions',
        null=True,
        blank=True,
    )
    destination_account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.PROTECT,
        related_name='incoming_transactions',
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    failure_reason = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.reference} ({self.status})'
