# Внутренние импорты
import random
import jwt
import requests
from typing import Type

# Импорты django
from django.contrib.auth import user_logged_in
from django.core.mail import send_mail

# RestFramework
from rest_framework_jwt.serializers import jwt_payload_handler

# Локальные импорты
from .models import Pin
from .models import EmailToken
from .serializers import UserSerializer

# импорты приложения
from everyservices import settings


def get_pin(length=5):
    return random.sample(range(10 ** (length - 1), 10 ** length), 1)[0]


def get_token(lenght=100):
    choices = "1234567890qwertyuiopasdfghjklzxcvbnm!@$%^"
    return (''.join(random.choice(choices) for i in range(lenght)))


def verify_pin(phone, pin):
    try:
        return str(pin) == str(Pin.objects.get(phone=phone).code)
    except Pin.DoesNotExist:
        return False


def verify_email_token(email, token):
    try:
        return str(token) == str(EmailToken.objects.get(email=email).token)
    except EmailToken.DoesNotExist:
        return False


def send_token(email):
    try:
        EmailToken.objects.get(email=email).delete()
    except EmailToken.DoesNotExist:
        pass

    token = get_token()
    EmailToken.objects.create(email=email, token=token)
    subject = "EVERYSERVICES. Подтверждение электронной почты"
    message = f"Для подтверждения своей личности перейдите по ссылке, указанной в этом письме:\n" \
              f"{settings.APPLICATION_ROOT_URL}authentication/aprmail/?t={token}&e={email}"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
    return {'detail': f'Сообщение для подтверждения почты отправлено по адресу {email}'}


def send_email_otc(email):
    try:
        EmailToken.objects.get(email=email).delete()
    except EmailToken.DoesNotExist:
        pass
    if settings.DEBUG:
        EmailToken.objects.create(email=email, token="1111")
        return {'detail': f'Сообщение для смены пароля отправлено по адресу {email}'}

    pin = get_pin()
    EmailToken.objects.create(email=email, token=pin)
    subject = "EVERYSERVICES. Восстановление пароля"
    message = f"Код:\n" \
              f"{pin}"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
    return {'detail': f'Сообщение для смены пароля отправлено по адресу {email}'}


def send_pin(phone):
    if Pin.objects.filter(phone=phone).exists():
        Pin.objects.get(phone=phone).delete()
    if settings.DEBUG:
        Pin(phone=phone, code=1111).save()
        return {'detail': 'Сообщение с кодом отправлено на номер %s' % phone}
    pin = get_pin()

    Pin(phone=phone, code=pin).save()
    url = f'{settings.SMS_SEND_URL}?text={pin}&number={phone}&sign={settings.SMS_SIGN_DEFAULT}'
    resp = requests.request(method='GET', url=url)
    if resp.status_code != 200:
        return {'detail': 'Введенный номер телефона не валиден.'}
    return {'detail': 'Сообщение с кодом отправлено на номер %s' % phone}


def get_auth_payload(user, request):
    try:
        payload = jwt_payload_handler(user)
        token = jwt.encode(payload, settings.SECRET_KEY)
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        user_data = UserSerializer(user).data
        if Pin.objects.filter(phone=user.phone).exists():
            Pin.objects.get(phone=user.phone).delete()
        return {"token": token, "user": user_data}
    except Exception as e:
        raise e


def check_name(name: str, e: Type[Exception]):
    if name is not None and name != "" and name.replace(" ", "") != "":
        return None
    raise e
