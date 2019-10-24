# from django.contrib import admin
from __future__ import annotations

from django.urls import path

from .views import ResourcesView


urlpatterns = [
    path(r'', ResourcesView.as_view({'post': 'create', 'get': 'list'})),
    path(r'/<int:pk>', ResourcesView.as_view({'get': 'retrieve', 'delete': 'destroy'})),
]
