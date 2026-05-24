from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:

        detail = response.data

        response.data = {
            "success": False,
            "error": {
                "code": response.status_code,
                "detail": detail
            }
        }

    return response