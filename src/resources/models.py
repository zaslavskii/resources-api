from __future__ import annotations

from django.contrib.auth.models import (
    AbstractBaseUser,
    AbstractUser,
    PermissionsMixin,
)
from django.db import models

from users.models import UserModel


__all__ = (
    'ResourceModel',
)


class ResourceModel(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    owner = models.ForeignKey(UserModel, editable=False, null=False, on_delete=models.PROTECT, related_name='resources')
