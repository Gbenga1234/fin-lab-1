from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from accounts.models import Account
from notifications.models import Notification

from .models import Transaction
from .tasks import process_transaction


class AccountAndTransferApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='sender',
            password='Safe-password-938!',
        )
        self.client.force_authenticate(self.user)

    def test_account_creation_ignores_client_balance(self):
        response = self.client.post(
            '/api/accounts/',
            {'currency': 'USD', 'balance': '500.00'},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['balance'], '0.00')
        self.assertEqual(Account.objects.get(pk=response.data['id']).owner, self.user)

    @patch('core.views.process_transaction.delay')
    def test_transfer_moves_funds_and_creates_notification(self, enqueue_task):
        source = Account.objects.create(owner=self.user, balance=Decimal('100.00'))
        destination = Account.objects.create(owner=self.user, balance=Decimal('5.00'))

        response = self.client.post(
            '/api/transactions/',
            {
                'reference': 'transfer-success-1',
                'source_account': source.pk,
                'destination_account': destination.pk,
                'amount': '30.00',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        enqueue_task.assert_called_once_with(response.data['id'])
        transfer = Transaction.objects.get(pk=response.data['id'])

        self.assertEqual(process_transaction.run(transfer.pk), Transaction.Status.COMPLETED)
        source.refresh_from_db()
        destination.refresh_from_db()
        transfer.refresh_from_db()
        self.assertEqual(source.balance, Decimal('70.00'))
        self.assertEqual(destination.balance, Decimal('35.00'))
        self.assertEqual(transfer.status, Transaction.Status.COMPLETED)
        self.assertEqual(Notification.objects.filter(recipient=self.user).count(), 1)

    def test_insufficient_funds_fail_without_changing_balances(self):
        source = Account.objects.create(owner=self.user, balance=Decimal('10.00'))
        destination = Account.objects.create(owner=self.user, balance=Decimal('2.00'))
        transfer = Transaction.objects.create(
            reference='transfer-failed-1',
            owner=self.user,
            source_account=source,
            destination_account=destination,
            amount=Decimal('20.00'),
            currency='USD',
        )

        self.assertEqual(process_transaction.run(transfer.pk), Transaction.Status.FAILED)
        source.refresh_from_db()
        destination.refresh_from_db()
        transfer.refresh_from_db()
        self.assertEqual(source.balance, Decimal('10.00'))
        self.assertEqual(destination.balance, Decimal('2.00'))
        self.assertEqual(transfer.failure_reason, 'Insufficient funds.')
        self.assertEqual(
            Notification.objects.get(recipient=self.user).kind,
            Notification.Kind.TRANSFER_FAILED,
        )

    def test_worker_rejects_non_positive_transfer_amounts(self):
        source = Account.objects.create(owner=self.user, balance=Decimal('10.00'))
        destination = Account.objects.create(owner=self.user, balance=Decimal('2.00'))
        transfer = Transaction.objects.create(
            reference='transfer-invalid-amount',
            owner=self.user,
            source_account=source,
            destination_account=destination,
            amount=Decimal('-1.00'),
            currency='USD',
        )

        self.assertEqual(process_transaction.run(transfer.pk), Transaction.Status.FAILED)
        source.refresh_from_db()
        destination.refresh_from_db()
        self.assertEqual(source.balance, Decimal('10.00'))
        self.assertEqual(destination.balance, Decimal('2.00'))

    def test_user_cannot_transfer_from_another_users_account(self):
        other_user = get_user_model().objects.create_user(
            username='other',
            password='Safe-password-938!',
        )
        source = Account.objects.create(owner=other_user)
        destination = Account.objects.create(owner=self.user)

        response = self.client.post(
            '/api/transactions/',
            {
                'reference': 'transfer-forbidden-1',
                'source_account': source.pk,
                'destination_account': destination.pk,
                'amount': '1.00',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)