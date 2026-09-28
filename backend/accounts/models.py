import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


def generate_account_number() -> str:
    return uuid.uuid4().hex[:16].upper()


class Account(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        LOCKED = 'locked', 'Locked'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='accounts',
    )
    account_number = models.CharField(max_length=16, unique=True, default=generate_account_number)
    currency = models.CharField(max_length=3, default='USD')
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=0),
                name='account_balance_nonnegative',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.account_number} ({self.currency})'