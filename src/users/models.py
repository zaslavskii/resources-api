from __future__ import annotations

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    UserManager,
)
from django.db import models


__all__ = (
    'UserModel',
    'UserOptionsModel',
)


class sentinel:
    pass


class UserModelManager(UserManager):
    """
    Manager to add support for createsuperuser cmd without having username field on the model.
    """

    def create_user(self, email=None, password=None, **extra_fields):
        return super().create_user(sentinel, email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return super().create_superuser(sentinel, email, password, **extra_fields)


class UserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', editable=False, unique=True)
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=150, blank=True)
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.'
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text=
        'Designates whether this user should be treated as active. '
        'Unselect this instead of deleting accounts.'

    )

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    objects = UserModelManager()

    def __init__(self, *args, **kwargs):
        """
        Workaround to support for create_superuser cmd
        """
        kwargs.pop('username', None)
        super().__init__(*args, **kwargs)


class UserOptionsModel(models.Model):
    user = models.OneToOneField(UserModel, editable=False, null=False, on_delete=models.CASCADE, related_name='options')
    quota = models.PositiveIntegerField(null=True)
