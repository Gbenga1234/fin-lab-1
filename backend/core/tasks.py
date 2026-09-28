from celery import shared_task
from django.db import transaction as db_transaction

from accounts.models import Account
from notifications.models import Notification

from .models import Transaction


@shared_task
def process_transaction(transaction_id: int) -> str:
    try:
        with db_transaction.atomic():
            transfer = Transaction.objects.select_for_update().get(pk=transaction_id)
            if transfer.status != Transaction.Status.PENDING:
                return transfer.status

            transfer.status = Transaction.Status.PROCESSING
            transfer.save(update_fields=['status', 'updated_at'])

            accounts = {
                account.pk: account
                for account in Account.objects.select_for_update()
                .filter(pk__in=[transfer.source_account_id, transfer.destination_account_id])
                .order_by('pk')
            }
            source = accounts.get(transfer.source_account_id)
            destination = accounts.get(transfer.destination_account_id)

            failure_reason = None
            if transfer.amount <= 0:
                failure_reason = 'Transfer amount must be greater than zero.'
            elif source is None or destination is None:
                failure_reason = 'A transfer account no longer exists.'
            elif source.status != Account.Status.ACTIVE or destination.status != Account.Status.ACTIVE:
                failure_reason = 'Both transfer accounts must be active.'
            elif source.currency != transfer.currency or destination.currency != transfer.currency:
                failure_reason = 'Transfer currency does not match both accounts.'
            elif source.balance < transfer.amount:
                failure_reason = 'Insufficient funds.'

            if failure_reason:
                transfer.status = Transaction.Status.FAILED
                transfer.failure_reason = failure_reason
                transfer.save(update_fields=['status', 'failure_reason', 'updated_at'])
                if transfer.owner_id:
                    Notification.objects.create(
                        recipient_id=transfer.owner_id,
                        transaction=transfer,
                        kind=Notification.Kind.TRANSFER_FAILED,
                        message=f'Transfer {transfer.reference} failed: {failure_reason}',
                    )
                return transfer.status

            source.balance -= transfer.amount
            destination.balance += transfer.amount
            source.save(update_fields=['balance'])
            destination.save(update_fields=['balance'])
            transfer.status = Transaction.Status.COMPLETED
            transfer.save(update_fields=['status', 'updated_at'])

            if transfer.owner_id:
                Notification.objects.create(
                    recipient_id=transfer.owner_id,
                    transaction=transfer,
                    kind=Notification.Kind.TRANSFER_COMPLETED,
                    message=f'Transfer {transfer.reference} completed.',
                )
            if destination.owner_id != transfer.owner_id:
                Notification.objects.create(
                    recipient_id=destination.owner_id,
                    transaction=transfer,
                    kind=Notification.Kind.TRANSFER_RECEIVED,
                    message=f'You received {transfer.amount} {transfer.currency}.',
                )

            return transfer.status
    except Transaction.DoesNotExist:
        return 'missing'
