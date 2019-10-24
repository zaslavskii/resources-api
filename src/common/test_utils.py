from __future__ import annotations

import random
import string

from django.test import Client
from rest_framework.test import APIClient

from users.models import UserModel, UserOptionsModel


def get_random_string(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def get_random_int(min_value: int = 0, max_value: int = 10000) -> str:
    return random.randint(min_value, max_value)


class UsersTestMixin:

    def setUp(self) -> None:
        self.user_email = f'{get_random_string()}@example.com'
        self.user_password = get_random_string()
        self.user = self.create_user(self.user_email, self.user_password)

        self.admin_email = f'{get_random_string()}@example.com'
        self.admin_password = get_random_string()
        self.admin = self.create_adminuser(self.admin_email, self.admin_password)

        self.user_client = self.get_authorized_client(self.user_email, self.user_password)
        self.admin_client = self.get_authorized_client(self.admin_email, self.admin_password)

    def create_user(self, email: str, password: str) -> UserModel:
        user = UserModel(email=email)
        user.set_password(password)
        user.save()
        UserOptionsModel.objects.create(user=user)

        return user

    def create_adminuser(self, email: str, password: str) -> UserModel:
        user = UserModel(email=email, is_staff=True)
        user.set_password(password)
        user.save()
        UserOptionsModel.objects.create(user=user)

        return user

    def get_authorized_client(self, email: str, password: str) -> Client:
        response = self.client.post('/api/v1/auth/login', {'email': email, 'password': password})
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.json()["access"]}')
        return client

    def generate_email(self) -> str:
        return f'{get_random_string()}@example.com'

    def generate_password(self) -> str:
        return get_random_string()
