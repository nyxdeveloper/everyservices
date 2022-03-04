# rest framework
from rest_framework.exceptions import APIException


class MasterIdRequired(APIException):
    default_detail = "Укажите идентификатор мастера"
    status_code = 400
