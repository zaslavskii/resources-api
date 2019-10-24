# from django.contrib import admin
from __future__ import annotations

from django.urls import path

from .views import (
    AuthViewSet,
    MeView,
    UsersOptionsView,
    UsersView,
)


users_urlpatterns = [
    path(r'/me', MeView.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'})),
    path(r'', UsersView.as_view({'post': 'create', 'get': 'list'})),
    path(r'/<int:pk>', UsersView.as_view({'get': 'retrieve', 'delete': 'destroy'})),
    path(r'/<int:pk>/options', UsersOptionsView.as_view({'get': 'retrieve',
                                                         'put': 'update',
                                                         'patch': 'partial_update'})),
]

auth_urlpatterns = [
    path(r'/register', AuthViewSet.as_view({'post': 'register'})),
    path(r'/login', AuthViewSet.as_view({'post': 'obtain_jwt'})),
]
