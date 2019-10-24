from __future__ import annotations

import typing as t

from django.db import transaction
from rest_framework import serializers

from users.models import UserModel, UserOptionsModel

from .models import ResourceModel


__all__ = (
    'CreateResourceSerializer',
    'DetailResourceSerializer',
    'ResourceQuotaExceeded',
)


class ResourceQuotaExceeded(Exception):
    def __init__(self, quota: int) -> None:
        self.quota = quota


class CreateResourceSerializer(serializers.ModelSerializer):
    owner_id = serializers.PrimaryKeyRelatedField(
        source='owner',
        queryset=UserModel.objects.all(),
        default=serializers.CreateOnlyDefault(serializers.CurrentUserDefault()),
    )

    class Meta:
        model = ResourceModel
        fields = ('pk', 'name', 'owner_id',)

    def _get_request_user(self) -> UserModel:
        return self.context["request"].user

    def validate_owner_id(self, owner: UserModel) -> UserModel:
        request_user = self._get_request_user()

        if not request_user.is_staff:
            return request_user

        return owner

    @transaction.atomic()
    def create(self, validated_data: t.Dict[str, t.Any]) -> ResourceModel:
        owner = validated_data['owner']
        options = UserOptionsModel.objects.filter(user_id=owner.id).select_for_update().get()

        if options.quota is not None and owner.resources.count() >= options.quota:
            raise ResourceQuotaExceeded(options.quota)

        return super().create(validated_data)


class DetailResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceModel
        fields = ('pk', 'name', 'owner_id',)
