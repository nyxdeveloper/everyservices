from django.db import models
from django.contrib.postgres.fields import ArrayField

from everyservices.settings import AUTH_USER_MODEL

import datetime


class SpecialSchedule(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="special_schedules")
    working = models.BooleanField(default=True)
    date = models.DateField()
    times = models.JSONField(default=None, null=True)

    class Meta:
        verbose_name = "Специальный график"
        verbose_name_plural = "Исключения из графиков"
        ordering = ["-date"]
        unique_together = [["user", "date"]]

    def __str__(self):
        return f"{self.user.name} ({self.date})"


class Schedule(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="schedules")
    start = models.DateField()
    schedule_days = ArrayField(models.BooleanField(default=True))

    schedule_time = models.JSONField()

    class Meta:
        verbose_name = "График"
        verbose_name_plural = "Графики работы"
        ordering = ["-start"]
        unique_together = [["user", "start"]]

    def __str__(self):
        return str(self.start)

    def get_day_schedule(self, date):
        """ Возвращает расписание на нужную дату """
        try:
            """
            Если на данную дату существует специальный график, возвращаем 
            расписание по специальному графику
            """
            special = SpecialSchedule.objects.get(user=self.user, date=date)
            working = special.working
            is_special = True
            ranges = special.times
        except SpecialSchedule.DoesNotExist:
            if date < self.start:
                """
                Если переданная дата меньше даты начала текущего графика, 
                возвращаем стандартный нерабочий день
                """
                return {
                    "date": date.strftime("%d.%m.%Y"),
                    "working": False,
                    "special": False,
                    "start": False,
                    "ranges": None
                }
            """
            Если специального графика на эту дату нет, возвращаем 
            расписание по текущему графику
            """
            rem = (abs(date - self.start).days % len(self.schedule_days))
            """
            Проверяем какое количество периодов вмещается в количество дней 
            между датой начала текущего графика и указанной датой.
            """
            if rem > 0:
                """
                Если в промежуток включается не целое количество периодов, берем 
                день, индекс которого равен по остатку от деления по модулю
                """
                working = self.schedule_days[rem]
                ranges = self.schedule_time[rem]
            else:
                """
                Если в промежуток входит целое число периодов, берем последний 
                день графика
                """
                working = self.schedule_days[0]
                ranges = self.schedule_time[0]
            is_special = False
        return {
            "date": date.strftime("%d.%m.%Y"),
            "working": working,
            "special": is_special,
            "start": self.start == date,
            "ranges": ranges
        }
