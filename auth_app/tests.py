
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')  # Replace 'signup' with the actual URL name if different

    def test_signup(self):
        # Test user signup
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }

        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure a token was created for the user
        user = User.objects.get(username='testuser')
        token = Token.objects.get(user=user)
        self.assertEqual(response.data['token'], token.key)

    def test_login(self):
        # Create a test user
        user = User.objects.create_user(username='testuser', password='testpassword')

        # Test user login
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }

        response = self.client.post(reverse('login'), data, format='json')  # Replace 'login' with the actual URL name if different
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    