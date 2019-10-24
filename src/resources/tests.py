from __future__ import annotations

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APITestCase

from common.test_utils import UsersTestMixin, get_random_string

from .models import ResourceModel


class ResourcesEndpointsTest(UsersTestMixin, APITestCase):
    def test_resources_create__user(self):
        name = get_random_string()

        response = self.user_client.post('/api/v1/resources', {'name': name})

        expected = {'name': name, 'owner_id': self.user.id}
        actual = response.json()

        assert response.status_code == HTTP_201_CREATED
        assert expected.items() <= actual.items()

    def test_resources_create_for_another_user__user(self):
        name = get_random_string()

        response = self.user_client.post('/api/v1/resources', {'name': name, 'owner_id': self.admin.id})

        expected = {'name': name, 'owner_id': self.user.id}
        actual = response.json()

        assert response.status_code == HTTP_201_CREATED
        assert expected.items() <= actual.items()

    def test_resources_create_when_quota_exceeded__user(self):
        name = get_random_string()

        self.user.options.quota = 0
        self.user.options.save()

        response = self.user_client.post('/api/v1/resources', {'name': name})

        assert response.status_code == HTTP_403_FORBIDDEN
        assert not ResourceModel.objects.filter(name=name).exists()

    def test_resources_get_list_only_owned__user(self):
        user_resource = ResourceModel(name=get_random_string(), owner=self.user)
        admin_resource = ResourceModel(name=get_random_string(), owner=self.admin)

        ResourceModel.objects.bulk_create([user_resource, admin_resource])

        response = self.user_client.get('/api/v1/resources')

        assert response.status_code == HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]['name'] == user_resource.name

    def test_resources_delete__user(self):
        user_resource = ResourceModel.objects.create(name=get_random_string(), owner=self.user)

        response = self.user_client.delete(f'/api/v1/resources/{user_resource.id}')

        assert response.status_code == HTTP_204_NO_CONTENT
        assert not ResourceModel.objects.filter(pk=user_resource.id).exists()

    def test_resources_create_admin(self):
        name = get_random_string()

        response = self.admin_client.post('/api/v1/resources', {'name': name})

        expected = {'name': name, 'owner_id': self.admin.id}
        actual = response.json()

        assert response.status_code == HTTP_201_CREATED
        assert expected.items() <= actual.items()

    def test_resources_create_for_another_user__admin(self):
        name = get_random_string()

        response = self.admin_client.post('/api/v1/resources', {'name': name, 'owner_id': self.user.id})

        expected = {'name': name, 'owner_id': self.user.id}
        actual = response.json()

        assert response.status_code == HTTP_201_CREATED
        assert expected.items() <= actual.items()

    def test_resources_create_when_quota_exceeded_for_another_user__admin(self):
        name = get_random_string()

        self.user.options.quota = 0
        self.user.options.save()

        response = self.admin_client.post('/api/v1/resources', {'name': name, 'owner_id': self.user.id})

        assert response.status_code == HTTP_403_FORBIDDEN
        assert not ResourceModel.objects.filter(name=name).exists()

    def test_resources_get_list__admin(self):
        user_resource = ResourceModel(name=get_random_string(), owner=self.user)
        admin_resource = ResourceModel(name=get_random_string(), owner=self.admin)

        ResourceModel.objects.bulk_create([user_resource, admin_resource])

        response = self.admin_client.get('/api/v1/resources')

        assert response.status_code == HTTP_200_OK
        assert len(response.json()) == 2

    def test_resources_get_list_filtered_by_owner__admin(self):
        user_resource = ResourceModel(name=get_random_string(), owner=self.user)
        admin_resource = ResourceModel(name=get_random_string(), owner=self.admin)

        ResourceModel.objects.bulk_create([user_resource, admin_resource])

        response = self.admin_client.get(f'/api/v1/resources?owner_id={self.user.id}')

        assert response.status_code == HTTP_200_OK
        assert len(response.json()) == 1

    def test_resources_delete_resource_of_another_user__admin(self):
        user_resource = ResourceModel.objects.create(name=get_random_string(), owner=self.user)

        response = self.admin_client.delete(f'/api/v1/resources/{user_resource.id}')

        assert response.status_code == HTTP_204_NO_CONTENT
        assert not ResourceModel.objects.filter(pk=user_resource.id).exists()
