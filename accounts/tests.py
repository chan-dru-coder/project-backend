from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsAuthTests(APITestCase):
    def test_user_registration(self):
        url = reverse('auth-register')
        payload = {
            'email': 'newpatient@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'PATIENT',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
            'phone_number': '+1-555-123-4567'
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertTrue(User.objects.filter(email='newpatient@example.com').exists())

    def test_user_login(self):
        User.objects.create_user(
            email='loginuser@example.com',
            password='TestPassword123!',
            first_name='Login',
            last_name='Tester'
        )
        url = reverse('auth-login')
        payload = {
            'email': 'loginuser@example.com',
            'password': 'TestPassword123!'
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)

    def test_health_check_endpoint(self):
        url = reverse('health-check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['database']['status'], 'healthy')
