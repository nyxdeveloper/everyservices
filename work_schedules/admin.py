# django
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Schedule
from .models import SpecialSchedule


class ScheduleAdmin(ModelAdmin):
    model = Schedule
    list_display = (
        'user', 'start',
    )
    list_filter = ('start',)
    fieldsets = (
        (None, {'fields': ('user', 'start', 'schedule_days', 'schedule_time')}),
    )
    search_fields = ('user__first_name', 'user__last_name', 'start',)
    ordering = (
        'user', 'start',
    )


class SpecialScheduleAdmin(ModelAdmin):
    model = SpecialSchedule
    list_display = (
        'user', 'working', 'date',
    )
    list_filter = ('working', 'date',)
    fieldsets = (
        (None, {'fields': ('user', 'working', 'schedule_days', 'schedule_time')}),
    )
    search_fields = ('user__first_name', 'user__last_name', 'date',)
    ordering = (
        'user', 'date', 'working',
    )


admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(SpecialSchedule, SpecialScheduleAdmin)
