from rest_framework.views import exception_handler
from rest_framework.response import Response
from domain.exceptions import DomainError

def custom_exception_handler(exc, context):
    # Сначала пробуем стандартный DRF handler
    response = exception_handler(exc, context)

    # Если это наше доменное исключение
    if isinstance(exc, DomainError):
        return Response(
            {
                "error": exc.error_code,
                "detail": str(exc),
            },
            status=exc.status_code,
        )

    return response