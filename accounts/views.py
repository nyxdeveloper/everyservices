# RestFramework
import datetime

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# django
from django.db import transaction
from django.utils import timezone
from django.shortcuts import render

# Локальные импорты
from .models import User
from .models import Pin
from .models import EmailToken
from .serializers import UserSerializer
from .services import verify_pin
from .services import verify_email_token
from .services import get_auth_payload
from .services import send_pin
from .services import send_token
from .services import send_email_otc
from everyservices.services import clean_phone
from .services import check_name
# исключения
from .exceptions import ExistingUserEmailException
from .exceptions import ExistingUserPhoneException
from .exceptions import InvalidPasswordException
from .exceptions import WrongLoginOrPasswordException
from .exceptions import UnapprovedEmailException
from .exceptions import UnapprovedPhoneException
from .exceptions import InvalidFirstNameException
from .exceptions import InvalidLastNameException


class Authentication(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @transaction.atomic
    @action(methods=["GET"], detail=False, url_path="aprmail")
    def apprmail(self, request):
        token = request.query_params.get("t")
        email = request.query_params.get("e")
        if verify_email_token(email, token):
            try:
                user = User.objects.get(email=email)
                user.approve_email = True
                user.save()
                return render(request, "email_approve_success.html")
            except User.DoesNotExist:
                return render(request, "email_approve_failed.html")
        return render(request, "email_approve_failed.html")

    @transaction.atomic
    @action(methods=["POST"], detail=False, url_path="reg")
    def registration(self, request):
        phone = request.data.get("phone")
        # проверяем наличие телефона
        if not phone:
            return Response({"detail": "Укажите телефон"}, status=status.HTTP_400_BAD_REQUEST)
        phone = clean_phone(phone)
        if User.objects.filter(phone=phone).exists():
            return Response({"detail": "Пользователь с таким номером телефона уже зарегистрирован в системе"},
                            status=400)
        pin = request.data.get("pin")
        if pin:
            if verify_pin(phone, pin):
                email = request.data.get("email")
                password = request.data.get("password")
                first_name = request.data.get("first_name")
                last_name = request.data.get("last_name")

                # очищаем номер телефона от лишнего
                phone = clean_phone(phone)

                try:
                    # проверяем есть ли пользователь с такой почтой
                    User.objects.get(email=email)
                    raise ExistingUserEmailException
                except User.DoesNotExist:
                    pass

                # проверяем есть ли пользователь с таким номером телефона
                if User.objects.filter(phone=phone).exists():
                    raise ExistingUserPhoneException

                # проверяем нет ли в пароле пробелов и есть ли в нем достаточное кол-во символов
                if " " in password or password == "" or len(password) < 6:
                    raise InvalidPasswordException

                user = User(phone=phone, email=email, first_name=first_name, last_name=last_name, approve_phone=True)
                user.set_password(password)
                user.save()
                if email:
                    # отправляем новому пользователю письмо для подтверждения почты
                    send_token(email)
                return Response({"detail": "Регистрация прошла успешно"}, status=status.HTTP_200_OK)
            return Response({"detail": "Неверный пин"}, status=status.HTTP_400_BAD_REQUEST)
        if Pin.objects.filter(phone=phone).exists():
            if Pin.objects.filter(phone=phone).first().created + datetime.timedelta(minutes=1) > timezone.now():
                return Response({"detail": "Новый код можно отправлять один раз в минуту"}, status=400)
        return Response(send_pin(phone), status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="auth")
    def authorization(self, request):
        login = request.data.get("login")
        password = request.data.get("password")

        if not login or not password:
            return Response({"detail": "Введите логин и пароль"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # пытаемся получить пользователя по логину
            if "@" in login:
                # если в качестве логина указан Email
                user = User.objects.get(email=login)
                # проверяем, подтвержден ли у человека Email
                if not user.approve_email:
                    raise UnapprovedEmailException
            else:
                # если в качестве логина указан телефон
                login = clean_phone(login)
                user = User.objects.get(phone=login)
                # проверяем, подтвержден ли у человека телефон
                if not user.approve_phone:
                    raise UnapprovedPhoneException
        except User.DoesNotExist:
            raise WrongLoginOrPasswordException
        if user.check_password(password):
            return Response(get_auth_payload(user, request), status=status.HTTP_200_OK)
        raise WrongLoginOrPasswordException

    @transaction.atomic
    @action(methods=["POST"], detail=False, url_path="approve_email")
    def approve_email(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Укажите Email"}, status=status.HTTP_400_BAD_REQUEST)
        return send_token(email)

    @transaction.atomic
    @action(methods=["POST"], detail=False, url_path="password_recovery")
    def password_recovery(self, request):
        login = request.data.get("login")
        otc = request.data.get("otc")
        password = request.data.get("password")

        if not login:
            return Response({"detail": "Укажите логин"}, status=status.HTTP_400_BAD_REQUEST)
        if otc:
            if not password:
                return Response({"detail": "Укажите пароль"}, status=400)
            try:
                if "@" in login:
                    if EmailToken.objects.filter(email=login, token=otc).exists():
                        EmailToken.objects.get(email=login, token=otc).delete()
                        user = User.objects.get(email=login)
                        user.set_password(password)
                        user.save()
                    else:
                        return Response({"detail": "Неверный код"}, status=400)
                else:
                    login = clean_phone(login)
                    if Pin.objects.filter(phone=login, code=otc).exists():
                        Pin.objects.get(phone=login, code=otc).delete()
                        user = User.objects.get(phone=login)
                        user.set_password(password)
                        user.save()
                    else:
                        return Response({"detail": "Неверный код"}, status=400)
            except User.DoesNotExist:
                return Response({"detail": "Неверный логин"}, status=400)
            return Response({"detail": "Пароль успешно изменен"}, status=200)
        try:
            if "@" in login:
                # если в качестве логина указан Email
                user = User.objects.get(email=login)
                # проверяем, подтвержден ли у человека Email
                if not user.approve_email:
                    raise UnapprovedEmailException
                return Response(send_email_otc(login))
            else:
                # если в качестве логина указан телефон
                login = clean_phone(login)
                user = User.objects.get(phone=login)
                # проверяем, подтвержден ли у человека телефон
                if not user.approve_phone:
                    raise UnapprovedPhoneException
                return Response(send_pin(login))
        except User.DoesNotExist:
            raise WrongLoginOrPasswordException

    @action(methods=["GET"], detail=False, url_path="otc_check")
    def otc_check(self, request):
        login = request.query_params.get("l")
        otc = request.query_params.get("c")
        if not login or not otc:
            return Response({"detail": "Для подтверждения отправьте логин и одноразовый код"}, status=400)
        if "@" in login:
            if EmailToken.objects.filter(email=login, token=otc).exists():
                return Response(status=200)
            else:
                return Response(status=404)
        else:
            if Pin.objects.filter(phone=login, code=otc).exists():
                return Response(status=200)
            else:
                return Response(status=404)


class Profile(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]

    @action(methods=["GET"], detail=False, url_path="info")
    def info(self, request):
        return Response(self.get_serializer(request.user, many=False).data)

    @transaction.atomic
    @action(methods=["POST"], detail=False, url_path="change_name")
    def change_name(self, request):
        user = request.user
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        check_name(first_name, InvalidFirstNameException)
        check_name(last_name, InvalidLastNameException)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return Response({"detail": f"Имя пользователя изменено на {user.name}"})

    @transaction.atomic
    @action(methods=["POST"], detail=False, url_path="change_avatar")
    def change_avatar(self, request):
        try:
            user = request.user
            user.avatar = request.FILES["file"]
            user.save()
            return Response({"detail": "Фотография успешно изменена"}, status=status.HTTP_200_OK)
        except KeyError:
            return Response({"detail": "Загрузите фотографию"}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(methods=["POST"], detail=False, url_path="change_phone")
    def change_phone(self, request):
        phone = request.data.get("phone")
        if not phone:
            return Response({"detail": "Укажите телефон"}, status=status.HTTP_400_BAD_REQUEST)
        phone = clean_phone(phone)
        if User.objects.filter(phone=phone).exists():
            return Response({"detail": "Пользователь с таким номером телефона уже зарегистрирован в системе"},
                            status=400)
        pin = request.data.get("pin")
        if pin:
            if verify_pin(phone, pin):
                try:
                    phone = clean_phone(phone)
                    user = request.user
                    user.phone = phone
                    user.approve_phone = True
                    user.save()
                    return Response({"detail": "Номер телефона успешно изменен"}, status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    return Response({"detail": "Пользователь не зарегистрирован"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": "Неверный пин"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(send_pin(phone))

    @transaction.atomic
    @action(methods=["POST"], detail=False, url_path="change_email")
    def change_email(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Укажите Email"}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        user.email = email
        user.save()
        return Response(send_token(email))

    @transaction.atomic
    @action(methods=["POST"], detail=False, url_path="change_password")
    def change_password(self, request):
        new_password = request.data.get("new_password")
        old_password = request.data.get("old_password")
        user = request.user
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Пароль успешно изменен на новый"}, status=status.HTTP_200_OK)
        return Response({"detail": "Неверный пароль"}, status=status.HTTP_403_FORBIDDEN)

    @transaction.atomic
    @action(methods=["POST"], detail=False, url_path="change_auto_confirm")
    def change_auto_confirm(self, request):
        auto_confirm = request.data.get("auto_confirm")
        user = request.user
        user.auto_confirm = auto_confirm
        user.save()
        return Response({"detail": "Пароль успешно изменен на новый"}, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(methods=["POST"], detail=False, url_path="delete_account")
    def delete_account(self, request):
        request.user.email = request.user.pk
        request.user.password = request.user.pk
        request.user.first_name = request.user.pk
        request.user.last_name = request.user.pk
        request.user.avatar = None
        request.user.save()
        return Response({"detail": "Аккаунт успешно удален"}, status=200)
