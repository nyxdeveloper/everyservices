# django
import random

from django.db import models

# внутренние импорты
import datetime
from datetime import timedelta

# импорты проекта
from everyservices.settings import AUTH_USER_MODEL

# локальные импорты
from .exception import NonFreeTimeException
from .exception import DayOffException


# def random_color(*args, **kwargs):
#     chars = "abcdef0123456789"
#     color = "#"
#     for i in range(6):
#         color += chars[random.randint(0, 15)]
#     return color

def random_color(*args, **kwargs):
    colors = [
        "#FF9900", "#CCCC00", "#FF9966", "#990000", "#FF9999", "#FF3366", "#FF66CC", "#990066", "#9933FF", "#9900FF",
        "#6633CC", "#330099", "#0033FF", "#0099FF", "#339999", "#006666", "#00FFFF", "#00CCCC", "#99FFCC", "#33CCCC",
        "#33CC99", "#33CC66", "#33FF66", "#339933", "#66CC33", "#669900"
    ]
    rand_index = random.randint(0, len(colors))
    return colors[rand_index - 1 if rand_index else 0]


class Record(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="records")
    service = models.ForeignKey("services.Service", on_delete=models.SET_NULL, null=True, related_name="records")
    client = models.ForeignKey("clients.Client", on_delete=models.SET_NULL, null=True, related_name="records")
    cost = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    duration = models.TimeField()
    recording_time = models.DateTimeField()
    end_time = models.DateTimeField()

    cancellation_reason = models.TextField(default="")
    color = models.CharField(default=random_color, max_length=7)

    comment = models.TextField(default="", blank=True, null=True)

    provided = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=True)
    was_rated = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи на услуги"
        ordering = ["-recording_time"]

    def __str__(self):
        return self.service.name

    def save(self, confirm_manually=False, *args, **kwargs):
        self.end_time = self.recording_time + timedelta(hours=self.duration.hour, minutes=self.duration.minute - 1)
        if self.time_is_busy():
            raise NonFreeTimeException
        if not self.user.is_working(self.recording_time.date()):
            raise DayOffException
        if not self.user.auto_confirm and not confirm_manually:
            self.confirmed = False
        return super(Record, self).save()

    def time_is_busy(self):
        return Record.objects.filter(user=self.user, canceled=True, confirmed=True).exclude(id=self.pk).filter(
            models.Q(recording_time__lte=self.recording_time, end_time__gte=self.recording_time) |
            models.Q(recording_time__gte=self.recording_time, end_time__lte=self.end_time) |
            models.Q(recording_time__lt=self.end_time, end_time__gte=self.end_time) |
            models.Q(recording_time__lte=self.recording_time, end_time__gte=self.end_time)
        ).exists()
