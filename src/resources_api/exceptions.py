from __future__ import annotations

import typing as t

from django.db import IntegrityError
from psycopg2 import errorcodes
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def get_api_exception_by_psycopg_exception(exc: t.Any) -> APIException:
    error_code = getattr(exc, 'pgcode', None)

    if error_code is None:
        return APIException()

    if error_code in (errorcodes.UNIQUE_VIOLATION, errorcodes.NOT_NULL_VIOLATION):
        return ValidationError(exc.pgerror)

    return APIException()


def handle_exception(exc: Exception, *args) -> Response:
    api_exception = exc

    if isinstance(exc, IntegrityError):
        api_exception = get_api_exception_by_psycopg_exception(exc.__cause__)

    return exception_handler(api_exception, *args)
