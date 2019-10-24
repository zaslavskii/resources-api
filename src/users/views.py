from __future__ import annotations

import typing as t

from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.permissions import (
    NOT,
    AllowAny,
    BasePermission,
    IsAdminUser,
    IsAuthenticated,
    SingleOperandHolder,
)
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

from users.seriazliers import AccessRefreshSerializer

from .models import UserModel, UserOptionsModel
from .seriazliers import (
    JWTTokenSerializer,
    MeSerializer,
    RegistrationSerializer,
    UserOptionsSerializer,
    UserSerializer,
)


__all__ = (
    'MeView',
    'AuthViewSet',
    'UsersView',
    'UsersOptionsView',
)


class AuthViewSet(GenericViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    action2permission_classes = {
        'register': [SingleOperandHolder(NOT, IsAuthenticated)],
    }

    def get_permissions(self) -> t.List[BasePermission]:
        perms_classes = self.action2permission_classes.get(self.action, self.permission_classes)
        return [p() for p in perms_classes]

    @swagger_auto_schema(request_body=RegistrationSerializer,
                         responses={status.HTTP_201_CREATED: AccessRefreshSerializer})
    def register(self, request: Request) -> JsonResponse:
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)

        jwt_serializer = JWTTokenSerializer(data=serializer.validated_data)
        jwt_serializer.is_valid()

        return JsonResponse(jwt_serializer.validated_data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=JWTTokenSerializer,
                         responses={status.HTTP_201_CREATED: AccessRefreshSerializer})
    def obtain_jwt(self, request: Request) -> JsonResponse:
        serializer = JWTTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return JsonResponse(serializer.validated_data, status=status.HTTP_201_CREATED)


class UsersView(mixins.RetrieveModelMixin,
                mixins.DestroyModelMixin,
                mixins.ListModelMixin,
                GenericViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)

    @swagger_auto_schema(request_body=RegistrationSerializer, responses={status.HTTP_201_CREATED: UserSerializer})
    def create(self, request: Request, *args: t.Any, **kwargs: t.Any) -> JsonResponse:
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)

        serializer_class = self.get_serializer_class()
        return JsonResponse(serializer_class(user).data, status=status.HTTP_201_CREATED)


class UsersOptionsView(mixins.UpdateModelMixin,
                       mixins.RetrieveModelMixin,
                       GenericViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = UserOptionsSerializer
    queryset = UserOptionsModel.objects.all()
    lookup_field = 'user_id'
    lookup_url_kwarg = 'pk'


class MeView(mixins.UpdateModelMixin,
             mixins.RetrieveModelMixin,
             GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = MeSerializer

    def get_object(self) -> UserModel:
        return self.request.user
