# rest framework
from rest_framework.exceptions import APIException
from rest_framework import status


class InvalidTimeRangeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Время начала работы не может быть больше времеени окончания"


class InvalidScheduleException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Убедитесь, что график заполнен верно"


class InvalidScheduleLenException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Количество дней должно совпадать с количеством расписаний"
