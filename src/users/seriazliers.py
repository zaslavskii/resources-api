from __future__ import annotations

import typing as t

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserModel, UserOptionsModel


__all__ = (
    'MeSerializer',
    'RegistrationSerializer',
    'JWTTokenSerializer',
    'UserSerializer',
    'UserOptionsSerializer',
    'AccessRefreshSerializer',
)


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(UserModel.objects.all(), message='User with such email already exists')
        ]
    )
    password = serializers.CharField(
        required=True,
        validators=(validate_password,),
        write_only=True
    )

    @transaction.atomic()
    def create(self, validated_data: t.Dict[str, t.Any]) -> UserModel:
        user = UserModel(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()

        UserOptionsModel.objects.create(user=user)

        return user

    def update(self, instance: UserModel, validated_data: t.Dict[str, t.Any]) -> None:
        raise NotImplementedError()


class AccessRefreshSerializer(serializers.Serializer):
    """
    Serializer for Swagger generation for auth endpoints
    """
    refresh = serializers.CharField()
    access = serializers.CharField()


class JWTTokenSerializer(TokenObtainPairSerializer):
    username_field = UserModel.USERNAME_FIELD


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('pk', 'email', 'first_name', 'last_name')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('pk', 'email', 'first_name', 'last_name', 'is_staff')


class UserOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOptionsModel
        fields = ('user_id', 'quota',)

    def _check_quota(self, quota: t.Optional[int], user: UserModel) -> None:
        # lock options row to avoid race condition between resource creation and options update
        UserOptionsModel.objects.filter(user_id=user.id).select_for_update().get()

        if quota is not None and user.resources.count() > quota:
            raise ValidationError({'quota': ['quota cannot be less than current number of resources']})

    @transaction.atomic()
    def update(self, instance: UserOptionsModel, validated_data: t.Dict[str, t.Any]) -> UserOptionsModel:
        if 'quota' in validated_data:
            self._check_quota(validated_data['quota'], self.context["request"].user)

        return super().update(instance, validated_data)
