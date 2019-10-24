from __future__ import annotations

import typing as t

from django.db.models import QuerySet
from rest_framework import mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from .models import ResourceModel
from .seriazliers import (
    CreateResourceSerializer,
    DetailResourceSerializer,
    ResourceQuotaExceeded,
)


class ResourcesView(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    GenericViewSet):
    queryset = ResourceModel.objects.all()
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('owner_id',)

    def get_serializer_class(self) -> t.Type[Serializer]:
        return {
            'create': CreateResourceSerializer,
        }.get(self.action, DetailResourceSerializer)

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        if self.request.user.is_staff:
            return super().filter_queryset(queryset)

        return super().filter_queryset(queryset).filter(owner=self.request.user)

    def create(self, request: Request, *args: t.Any, **kwargs: t.Any) -> Response:
        try:
            return super().create(request, *args, **kwargs)

        except ResourceQuotaExceeded as exc:
            raise PermissionDenied(f'Maximum number of resources is reached: {exc.quota}')
