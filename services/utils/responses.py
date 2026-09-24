from rest_framework.response import Response


def success_response(data=None, message="Request successful", status=200):
    return Response(
        {
            "success": True,
            "message": message,
            "error_code": None,
            "data": data,
        },
        status=status,
    )


def error_response(
    message="Something went wrong",
    error_code="GENERAL_ERROR",
    status=400,
):
    return Response(
        {
            "success": False,
            "message": message,
            "error_code": error_code,
            "data": None,
        },
        status=status,
    )
