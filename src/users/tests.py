from __future__ import annotations

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APITestCase

from common.test_utils import UsersTestMixin, get_random_int
from users.models import UserOptionsModel

from .models import UserModel


class AuthEndpointsTest(UsersTestMixin, APITestCase):
    def test_register__not_authorized(self):
        email = self.generate_email()
        password = self.generate_password()

        response = self.client.post('/api/v1/auth/register',
                                    {'email': email, 'password': password})

        assert response.status_code == HTTP_201_CREATED
        assert 'access' in response.json()
        assert 'refresh' in response.json()
        assert UserModel.objects.filter(email=email).exists()

    def test_register__authorized(self):
        response = self.user_client.post('/api/v1/auth/register',
                                         {'email': self.user_email, 'password': self.user_password})

        assert response.status_code == HTTP_403_FORBIDDEN

    def test_login__not_authorized(self):
        response = self.client.post('/api/v1/auth/login',
                                    {'email': self.user_email, 'password': self.user_password})

        assert response.status_code == HTTP_201_CREATED
        assert 'access' in response.json()
        assert 'refresh' in response.json()

    def test_login__authorized(self):
        response = self.user_client.post('/api/v1/auth/login',
                                         {'email': self.user_email, 'password': self.user_password})

        assert response.status_code == HTTP_201_CREATED
        assert 'access' in response.json()
        assert 'refresh' in response.json()


class UsersEndpointsTest(UsersTestMixin, APITestCase):
    def test_me(self):
        response = self.user_client.get('/api/v1/users/me')

        expected = {
            'pk': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        actual = response.json()

        assert response.status_code == HTTP_200_OK
        assert actual == expected

    def test_users_list__admin(self):
        response = self.admin_client.get('/api/v1/users')

        assert response.status_code == HTTP_200_OK
        assert len(response.json()) == UserModel.objects.count()

    def test_users_list__user(self):
        response = self.user_client.get('/api/v1/users')

        assert response.status_code == HTTP_403_FORBIDDEN

    def test_users_create__admin(self):
        email = self.generate_email()
        password = self.generate_password()

        response = self.admin_client.post('/api/v1/users', {'email': email, 'password': password})

        assert response.status_code == HTTP_201_CREATED
        assert response.json()['email'] == email
        assert UserModel.objects.filter(email=email).exists()
        assert UserOptionsModel.objects.filter(user__email=email).exists()

    def test_users_create__user(self):
        email = self.generate_email()
        password = self.generate_password()

        response = self.user_client.post('/api/v1/users', {'email': email, 'password': password})

        assert response.status_code == HTTP_403_FORBIDDEN

    def test_users_retrieve__admin(self):
        response = self.admin_client.get(f'/api/v1/users/{self.user.id}')

        assert response.status_code == HTTP_200_OK
        assert response.json()['email'] == self.user.email

    def test_users_retrieve__user(self):
        response = self.user_client.get(f'/api/v1/users/{self.admin.id}')

        assert response.status_code == HTTP_403_FORBIDDEN

    def test_users_delete__admin(self):
        response = self.admin_client.delete(f'/api/v1/users/{self.user.id}')

        assert response.status_code == HTTP_204_NO_CONTENT
        assert not UserModel.objects.filter(email=self.user_email).exists()

    def test_users_delete__user(self):
        response = self.user_client.delete(f'/api/v1/users/{self.admin.id}')

        assert response.status_code == HTTP_403_FORBIDDEN

    def test_users_options__user(self):
        response = self.user_client.get(f'/api/v1/users/{self.user.id}/options')

        assert response.status_code == HTTP_403_FORBIDDEN

    def test_users_options__get_quota__admin(self):
        response = self.admin_client.get(f'/api/v1/users/{self.user.id}/options')

        assert response.status_code == HTTP_200_OK
        assert response.json()['quota'] is None

    def test_users_options__set_quota__admin(self):
        new_quota = get_random_int(0, 100)

        response = self.admin_client.patch(f'/api/v1/users/{self.user.id}/options', {'quota': new_quota})

        assert response.status_code == HTTP_200_OK
        assert response.json()['quota'] == new_quota

    def test_users_options__set_user__admin(self):
        new_user = get_random_int(0, 100)

        response = self.admin_client.patch(f'/api/v1/users/{self.user.id}/options', {'user_id': new_user})

        assert response.status_code == HTTP_200_OK
        assert response.json()['user_id'] != new_user
