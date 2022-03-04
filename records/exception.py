# rest framework
from rest_framework.exceptions import APIException
from rest_framework import status


class NonFreeTimeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Данное время занято другим сеансом"


class DayOffException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Вы не работаете в этот день"
