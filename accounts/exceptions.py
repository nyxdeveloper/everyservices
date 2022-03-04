# rest framework
from rest_framework.exceptions import APIException
from rest_framework import status


class ExistingUserPhoneException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Пользователь с таким номером телефона уже зарегистрирован в системе"
    default_code = 'detail'


class ExistingUserEmailException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Пользователь с таким Email уже зарегистрирован в системе"
    default_code = 'detail'


class InvalidPasswordException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Пароль должен состоять минимум из 6 символов и не включать пробелы"
    default_code = 'detail'


class WrongLoginOrPasswordException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Неверный логин или пароль"
    default_code = 'detail'


class UnapprovedEmailException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Для выполнения действия подтвердите почту"
    default_code = 'detail'


class UnapprovedPhoneException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Для выполнения действия подтвердите телефон"
    default_code = 'detail'


class InvalidFirstNameException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Имя должно включать в себя как минимум один непробельный символ"
    default_code = 'detail'


class InvalidLastNameException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Фамилия должна включать в себя как минимум один непробельный символ"
    default_code = 'detail'
