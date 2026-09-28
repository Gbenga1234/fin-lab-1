from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class IdentityApiTests(APITestCase):
    def test_register_login_and_get_current_user(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'casey',
                'email': 'casey@example.com',
                'password': 'Safe-password-938!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        user = get_user_model().objects.get(username='casey')
        self.assertTrue(user.check_password('Safe-password-938!'))

        response = self.client.post(
            '/api/auth/login/',
            {'username': 'casey', 'password': 'Safe-password-938!'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")

        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'casey')

        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, 204)
        response = self.client.get('/api/auth/me/')
        self.assertIn(response.status_code, [401, 403])

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'missing', 'password': 'wrong'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)