import json
from rest_framework.response import Response
from rest_framework import status
from config.settings.conf import app_config
from src.serializer import GenericResponseSerializer


def make_response(
    message: str, status_code: int = status.HTTP_200_OK, success: bool = True
):
    return make_json_response({}, message, status_code, success)


def make_json_response(
    data, message: str = "", status_code: int = status.HTTP_200_OK, success: bool = True
):
    response_data = {
        "success": success,
        "message": message,
        "data": data,
        "latest_version": app_config.LATEST_VERSION,
        "acceptable_version": app_config.ACCEPTABLE_VERSION,
    }

    res_serializer = GenericResponseSerializer(data=response_data)
    if res_serializer.is_valid():
        return Response(res_serializer.data, status_code)
    else:
        return Response(res_serializer.errors, status.HTTP_500_INTERNAL_SERVER_ERROR)


def make_json_response_for_socket(
    data, message: str = "", event=None, status_code: int = status.HTTP_200_OK, success: bool = True
):
    return json.dumps(
        {
            "success": success,
            "message": message,
            "event": event,
            "data": data,
            "latest_version": app_config.LATEST_VERSION,
            "acceptable_version": app_config.ACCEPTABLE_VERSION,
        }
    )
