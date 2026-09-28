from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from notifications.models import Notification


class NotificationApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.recipient = user_model.objects.create_user(username='recipient', password='test')
        self.other_user = user_model.objects.create_user(username='other', password='test')
        self.notification = Notification.objects.create(
            recipient=self.recipient,
            kind=Notification.Kind.TRANSFER_COMPLETED,
            message='Transfer completed.',
        )

    def test_users_only_see_and_mark_their_own_notifications(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        response = self.client.post(f'/api/notifications/{self.notification.pk}/read/')
        self.assertEqual(response.status_code, 404)

        self.client.force_authenticate(self.recipient)
        response = self.client.post(f'/api/notifications/{self.notification.pk}/read/')
        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertIsNotNone(self.notification.read_at)