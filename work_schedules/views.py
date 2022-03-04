# rest framework
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# django
from django.db.models import Q
from django.utils import timezone

# локальные импорты
from .models import SpecialSchedule
from .models import Schedule
from .services import get_month_boundaries
from .services import get_datelist
from .services import convert_worktime_ranges
from .services import convert_worktime_range
from .serializers import SpecialScheduleSerializer
from .serializers import ScheduleSerializer

# внутренние импорты
import datetime
from typing import List

# импорты проекта
from everyservices.pagination import StandardResultsSetPagination


class ScheduleViewSet(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        now = timezone.now().date()
        actual = self.request.user.get_schedule(now)
        return self.queryset.filter(user=self.request.user, start__gte=actual.start if actual else now)

    @action(methods=["GET"], detail=False, url_path=r"actual/(?P<year>\d+)/(?P<month>\d+)")
    def get_schedule(self, request, year, month):
        """
        Возвращает календарь с расписанием на месяц
        """

        start_month, end_month = get_month_boundaries(int(year), int(month))  # начало и конец месяца
        days = get_datelist(start_month, end_month)  # дни месяца
        if self.get_queryset().filter(start__lte=start_month).exists():
            """
            Если существуют графики работы, начало которых раньше 
            начала указанного месяца, то вернуть тот из них, который 
            начинается позже всех
            """
            current_schedule = self.get_queryset().filter(start__lte=start_month).order_by("-start").first()
        elif self.get_queryset().filter(start__lte=end_month).exists():
            """
            Если существуют графики работы, начало которых раньше 
            конца указанного месяца, то вернуть тот из них, который 
            начинается позже всех
            """
            current_schedule = self.get_queryset().filter(start__lte=end_month).order_by("-start").first()
        else:
            """
            Если нет ни одних, ни других, вернуть тот, что начинается 
            раньше всех
            """
            try:
                current_schedule = self.get_queryset().order_by("start").first()
                if not current_schedule:
                    # resp = []
                    # for day in days:
                    #     resp.append({
                    #         "date": day.strftime("%d.%m.%Y"),
                    #         "working": True,
                    #         "special": request.user.special_schedules.filter(date=day).exists(),
                    #         "start": False,
                    #         "ranges": ["09:00-18:00"]
                    #     })
                    return Response([])
                    # return Response({"detail": "График не настроен"}, status=status.HTTP_404_NOT_FOUND)
            except self.queryset.model.DoesNotExist:
                """
                Если графиков вообще нет, возвращаем ошибку
                """
                # resp = []
                # for day in days:
                #     resp.append({
                #         "date": day.strftime("%d.%m.%Y"),
                #         "working": True,
                #         "special": request.user.special_schedules.filter(date=day).exists(),
                #         "start": False,
                #         "ranges": ["09:00-18:00"]
                #     })
                return Response([])
                # return Response({"detail": "График не настроен"}, status=status.HTTP_404_NOT_FOUND)
        try:
            next_start = current_schedule.get_next_by_start().start
        except self.queryset.model.DoesNotExist:
            next_start = None

        resp = []

        for day in days:
            if day == next_start:
                """
                Если дата равна дате начала следующего графика, 
                устанавливаем в качестве текущего графика следующий
                """
                current_schedule = current_schedule.get_next_by_start()
                try:
                    next_start = current_schedule.get_next_by_start().start
                except self.queryset.model.DoesNotExist:
                    next_start = None
            resp.append(current_schedule.get_day_schedule(day))
        return Response(resp, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="new")
    def new(self, request):
        """
        Создает новый график работы
        """
        start = request.data.get("start")
        try:
            start = datetime.datetime.strptime(start, "%d.%m.%Y").strftime("%Y-%m-%d")
            start = datetime.datetime.strptime(start, "%Y-%m-%d")
        except ValueError:
            return Response({"detail": "Дата должна иметь формат дд.мм.ГГГГ"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            schedule_days: List[bool] = request.data.get("schedule_days")
            schedule_time: List[List] = request.data.get("schedule_time")
            if len(schedule_days) != len(schedule_time):
                return Response({"detail": "Дни и расписания должны совпадать"}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({"detail": "Убедитесь, что график заполнен верно"}, status=status.HTTP_400_BAD_REQUEST)
        if not convert_worktime_ranges(schedule_time):
            return Response({"detail": "Убедитесь, что график заполнен верно"}, status=status.HTTP_400_BAD_REQUEST)
        Schedule.objects.create(
            user=request.user,
            start=start,
            schedule_days=schedule_days,
            schedule_time=schedule_time
        )
        return Response({"detail": "График успешно изменен"}, status=status.HTTP_200_OK)


class SpecialSchedulesViewSet(ModelViewSet):
    queryset = SpecialSchedule.objects.all()
    serializer_class = SpecialScheduleSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user, date__gte=timezone.now().date())

    @action(methods=["POST"], detail=False, url_path="new")
    def new(self, request):
        """
        Создает специальный график работы
        """
        working = request.data.get("working")
        times = request.data.get("times")
        if not convert_worktime_range(times) and working:
            return Response({"detail": "Убедитесь, что график заполнен верно"}, status=status.HTTP_400_BAD_REQUEST)
        date = request.data.get("date")
        try:
            date = datetime.datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
            if request.user.special_schedules.filter(date=date).exists():
                return Response({"detail": "На данную дату уже существует специальный график"}, status=400)
        except ValueError:
            return Response({"detail": "Укажите правильный формат даты"}, status=status.HTTP_400_BAD_REQUEST)
        SpecialSchedule.objects.create(
            user=request.user,
            working=working,
            date=date,
            times=times
        )
        return Response({"detail": f"На {date} составлен специальный график"}, status=status.HTTP_200_OK)

    @action(methods=["PUT"], detail=False, url_path=r"edit")
    def edit(self, request):
        date = request.query_params.get("date")
        working = request.data.get("working")
        times = request.data.get("times")
        if not convert_worktime_range(times) and working:
            return Response({"detail": "Убедитесь, что график заполнен верно"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            date = datetime.datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
        except ValueError:
            return Response({"detail": "Укажите правильный формат даты"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            schedule = self.get_queryset().get(date=date)
            schedule.working = working
            schedule.times = times
            schedule.save()
            return Response({"detail": f"График на {date} успешно отредактирован"}, status=status.HTTP_200_OK)
        except SpecialSchedule.DoesNotExist:
            return Response({"detail": "Объект не найден"}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=["DELETE"], detail=False, url_path=r"remove")
    def remove(self, request):
        date = request.query_params.get("date")
        try:
            date = datetime.datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
        except ValueError:
            return Response({"detail": "Укажите правильный формат даты"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.get_queryset().get(date=date).delete()
        except self.queryset.model.DoesNotExist:
            return Response({"detail": "Объект не найден"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
