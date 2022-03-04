# rest framework
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

# django
from django.db import transaction

# сторонние зависимости
from django_filters.rest_framework import DjangoFilterBackend

# внутренние зависимости
import datetime
import re

# локальные импорты
from .models import Record
from .serializers import RecordSerializer
from .services import get_free_times
from .services import records_datetime_filter

# импорты проекта
from everyservices.pagination import StandardResultsSetPagination


class RecordViewSet(ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]
    filterset_fields = ["service", "client", "provided", "canceled", "confirmed", "recording_time"]
    search_fields = ["service__name", "client__name", "cost"]
    ordering_fields = ["service", "client", "cost", "duration", "recording_time"]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def filter_queryset(self, queryset):
        queryset = records_datetime_filter(queryset, self.request)
        return super(RecordViewSet, self).filter_queryset(queryset)

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
        serializer.instance.confirmed = True
        serializer.instance.save(confirm_manually=True)

    def list(self, request, *args, **kwargs):
        if request.query_params.get("count") is not None:
            return Response({"count": self.filter_queryset(self.get_queryset()).count()})
        return super(RecordViewSet, self).list(request, *args, **kwargs)

    @action(methods=["GET"], detail=False, url_path="recording_time")
    def get_recording_time_list(self, request):
        date = request.query_params.get("date")
        duration = request.query_params.get("duration")
        exclude = request.query_params.getlist("ex")
        if not date or not duration:
            return Response({"detail": "Укажите дату и длительность услуги"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            date = datetime.datetime.strptime(date, "%d.%m.%Y").date()
            duration = datetime.datetime.strptime(duration, "%H:%M").time()
        except ValueError:
            return Response({"detail": "Укажите правильную дату и длительность"}, status=status.HTTP_400_BAD_REQUEST)
        free_times = get_free_times(request.user, date, duration, exclude=[ex for ex in exclude if ex])
        return Response([t.strftime("%H:%M") for t in free_times], status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path=r"cancel/(?P<pk>\d+)")
    def cancel_record(self, request, pk):
        cancellation_reason = request.data.get("cancellation_reason")
        try:
            instance = self.get_queryset().get(pk=pk)
            instance.canceled = True
            instance.cancellation_reason = cancellation_reason
            instance.save()
            return Response({"detail": "Запись отменена"}, status=status.HTTP_200_OK)
        except Record.DoesNotExist:
            return Response({"detail": "Запись не найдена"}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=["POST"], detail=False, url_path=r"provide/(?P<pk>\d+)")
    def provide_record(self, request, pk):
        try:
            instance = self.get_queryset().get(pk=pk)
            instance.provided = True
            instance.save()
            return Response({"detail": "Услуга завершена"}, status=status.HTTP_200_OK)
        except Record.DoesNotExist:
            return Response({"detail": "Запись не найдена"}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=["POST"], detail=False, url_path=r"confirm/(?P<pk>\d+)")
    def confirm_record(self, request, pk):
        try:
            instance = self.get_queryset().get(pk=pk)
            instance.confirmed = True
            instance.save(confirm_manually=True)
            return Response({"detail": "Запись подтверждена"}, status=status.HTTP_200_OK)
        except Record.DoesNotExist:
            return Response({"detail": "Запись не найдена"}, status=status.HTTP_404_NOT_FOUND)
