# внутренние зависимости
import datetime
from typing import List

# локальные зависимости
from .exceptions import InvalidTimeRangeException
from .exceptions import InvalidScheduleException
from .exceptions import InvalidScheduleLenException

# количество дней в месяцах
num_days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def get_month_boundaries(year, month):
    return [datetime.date(year, month, 1), datetime.date(year, month, num_days[month - 1])]


def get_datelist(start, end):
    return [start + datetime.timedelta(days=i) for i in range((end - start).days + 1)]


def convert_worktime_range(l):
    nl = []
    if not l:
        return None
    for i in l:
        t_start, t_end = i.split("-")
        t_start = datetime.datetime.strptime(t_start, "%H:%M")
        t_end = datetime.datetime.strptime(t_end, "%H:%M")
        if t_start > t_end:
            raise InvalidTimeRangeException
        nl.append([t_start, t_end])
    return nl


def convert_worktime_ranges(l: list):
    try:
        nl = []
        for i in l:
            nl.append(convert_worktime_range(i))
    except (ValueError, KeyError):
        return None
    return nl


def check_schedule_data(data):
    try:
        schedule_days: List[bool] = data["schedule_days"]
        schedule_time: List[List] = data["schedule_time"]
        if len(schedule_days) != len(schedule_time):
            raise InvalidScheduleLenException
    except TypeError:
        raise InvalidScheduleException
    if not convert_worktime_ranges(schedule_time):
        raise InvalidScheduleException


def check_special_schedule_data(data):
    try:
        times: List[str] = data["times"]
    except TypeError:
        raise InvalidScheduleException
    if not convert_worktime_range(times):
        raise InvalidScheduleException
