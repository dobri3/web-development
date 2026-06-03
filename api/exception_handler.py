from rest_framework.views import exception_handler
from rest_framework.response import Response

from domain.exceptions import DomainError


STATUS_CODE_TO_ERROR_CODE = {
    400: "BAD_REQUEST",
    401: "AUTHENTICATION_FAILED",
    403: "PERMISSION_DENIED",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    415: "UNSUPPORTED_MEDIA_TYPE",
    429: "THROTTLED",
    500: "INTERNAL_SERVER_ERROR",
}


def get_error_code(response):
    return STATUS_CODE_TO_ERROR_CODE.get(
        response.status_code,
        "API_ERROR",
    )


def custom_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        response_body = {
            "success": False,
            "error": {
                "code": exc.error_code,
                "detail": str(exc),
                "status_code": exc.status_code,
            },
        }

        return Response(response_body, status=exc.status_code)

    response = exception_handler(exc, context)

    if response is None:
        return None

    response_body = {
        "success": False,
        "error": {
            "code": get_error_code(response),
            "detail": response.data,
            "status_code": response.status_code,
        },
    }

    return Response(response_body, status=response.status_code)