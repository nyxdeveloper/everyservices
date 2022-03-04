# django
from django.db.models import Q

# локальные импорты
from .exception import DayOffException

# внутренние зависимости
import datetime


def records_datetime_filter(queryset, request):
    time = request.query_params.get("time")
    date = request.query_params.get("date")
    if time:
        h = int(time.split(":")[0])
        m = int(time.split(":")[1])
        queryset = queryset.filter(recording_time__hour=h, recording_time__minute=m)
    if date:
        d = int(date.split(".")[0])
        m = int(date.split(".")[1])
        y = int(date.split(".")[2])
        queryset = queryset.filter(recording_time__day=d, recording_time__month=m, recording_time__year=y)
    return queryset


def get_free_times(user, date, duration, step=None, exclude: list = None):
    if not step:
        step = user.min_record_time  # время на оказание услуги с минимальной длительностью
    if not user.is_working(date):
        raise DayOffException
    schedule_times = user.get_schedule_times(date)
    records = user.records.filter(
        confirmed=True,
        recording_time__year=date.year,
        recording_time__month=date.month,
        recording_time__day=date.day
    ).exclude(id__in=exclude if exclude else []).values("recording_time", "end_time")
    free_times = []

    for st in schedule_times:
        st = st.split("-")
        t_start = datetime.datetime.strptime(st[0], "%H:%M")
        t_end = datetime.datetime.strptime(st[1], "%H:%M")
        tx = t_start
        for r in records.filter(recording_time__time__gte=t_start, recording_time__time__lte=t_end).order_by(
                "recording_time").values_list("recording_time", "end_time"):
            r_start = r[0]
            r_end = r[1]
            while (tx + datetime.timedelta(hours=duration.hour, minutes=duration.minute)).time() <= r_start.time():
                free_times.append(tx)
                tx += step
            tx = r_end
        while (tx + datetime.timedelta(hours=duration.hour, minutes=duration.minute)).time() <= t_end.time():
            free_times.append(tx)
            tx += step
    return free_times
