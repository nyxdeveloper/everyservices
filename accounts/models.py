# Внутренние импорты
import uuid
import datetime

# Импорты django
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db import transaction
from django.utils import timezone

# локальные импорты
from .choices import SERVICE_PACKAGES


def avatar_filepath(instance, filename):
    return f"avatars/{instance.pk}/{filename}"


class UserManager(BaseUserManager):

    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError('The given username must be set')
        try:
            with transaction.atomic():
                user = self.model(phone=phone, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except:
            raise

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(phone, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # chars
    phone = models.CharField(verbose_name='Номер телефона', null=False, blank=False, unique=True, max_length=15)
    email = models.EmailField(verbose_name='Email', default=None, null=True, blank=True)
    password = models.CharField(max_length=128, blank=True, default="")
    first_name = models.CharField(max_length=30, blank=True, default=None, null=True)
    last_name = models.CharField(max_length=30, blank=True, default=None, null=True)
    service_package = models.CharField(max_length=20, choices=SERVICE_PACKAGES, default=SERVICE_PACKAGES[0])

    # files
    avatar = models.ImageField(upload_to=avatar_filepath, blank=True, null=True, default=None)

    # booleans
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    approve_email = models.BooleanField(default=False)
    approve_phone = models.BooleanField(default=False)
    auto_confirm = models.BooleanField(default=True)

    # dates
    date_joined = models.DateTimeField(auto_now_add=True)
    date_last_change_email = models.DateTimeField(default=None, null=True)
    date_last_change_phone = models.DateTimeField(default=None, null=True)
    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.name

    @property
    def rating(self):
        rating = self.grades.all()
        try:
            return rating.aggregate(models.Sum('grade'))['grade__sum'] / rating.count()
        except (TypeError, ZeroDivisionError):
            return 5.0

    @property
    def name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return '#USER_%s' % self.phone

    def check_login(self, login):
        if "@" in login:
            return self.approve_email
        return self.approve_phone

    def get_special_schedule(self, date):
        try:
            return self.special_schedules.get(date=date)
        except self.special_schedules.model.DoesNotExist:
            return None

    def get_schedule(self, date):
        try:
            return self.schedules.filter(start__lte=date).order_by("-start").first()
        except self.schedules.model.DoesNotExist:
            return None

    def get_actual_schedule(self, date):
        schedule = self.get_special_schedule(date)
        if schedule:
            return [True, schedule]
        schedule = self.get_schedule(date)
        if schedule:
            return [False, schedule]
        return None

    def is_working(self, date):
        special, schedule = self.get_actual_schedule(date)
        if special:
            return schedule.working
        return schedule.get_day_schedule(date)["working"]

    def get_schedule_times(self, date):
        special, schedule = self.get_actual_schedule(date)
        if special:
            return schedule.times
        return schedule.get_day_schedule(date)["ranges"]

    @property
    def min_record_time(self):
        shortest_service = self.services.order_by("duration").first()
        if shortest_service:
            return datetime.timedelta(hours=shortest_service.duration.hour, minutes=shortest_service.duration.minute)
        return datetime.timedelta(hours=0, minutes=5)


class Grade(models.Model):
    GRADES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    client = models.CharField(max_length=250)
    assessed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    grade = models.PositiveIntegerField(verbose_name='Оценка', choices=GRADES)
    comment = models.TextField(verbose_name='Комментарий', blank=True, default='')
    created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True, editable=False)

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

    def __str__(self):
        return f'{self.assessed} ({self.grade})'


class Pin(models.Model):
    phone = models.CharField(max_length=13, primary_key=True, unique=True, db_index=True)
    code = models.CharField(max_length=10)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Пин'
        verbose_name_plural = 'Пинкоды'

    def __str__(self):
        return self.phone


class EmailToken(models.Model):
    email = models.EmailField(primary_key=True)
    token = models.TextField()

    class Meta:
        verbose_name = "Токен"
        verbose_name_plural = "Одноразовые почтовые токены"

    def __str__(self):
        return self.email
