# rest framework
import datetime

from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# django
from django.utils import timezone
from django.db.models import Sum

# локальные импорты
from .exceptions import InvalidFilter

# импорты приложений
from records.models import Record


class ReportViewSet(GenericViewSet):
    queryset = Record.objects.all()
    serializer_class = None
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_report_filters(self, t, *args):
        filters = []
        for a in args:
            try:
                f = self.request.query_params.get(a)
                filters.append(t(f))
            except (TypeError, ValueError):
                raise InvalidFilter(f"Фильтр {a} должен быть передан в формате {t.__name__}. Вы передали: '{f}'")
        if len(filters) < 1:
            return []
        return filters if len(filters) > 1 else filters[0]

    @action(methods=["GET"], detail=False, url_path="records")
    def records_report(self, request):
        year, month = self.get_report_filters(int, "year", "month")
        records = self.get_queryset().filter(confirmed=True, end_time__month=month, end_time__year=year)
        all_count = records.count()
        provided_count = records.filter(provided=True).count()
        canceled_count = records.filter(canceled=True).count()
        profit = records.filter(provided=True).aggregate(Sum("cost"))["cost__sum"]
        return Response({
            "all_count": all_count,
            "provided_count": provided_count,
            "canceled_count": canceled_count,
            "profit": profit
        })

    @action(methods=["GET"], detail=False, url_path="clients")
    def clients_report(self, request):
        year, month = self.get_report_filters(int, "year", "month")

        clients = request.user.clients.all()
        all_count = clients.count()
        per_month = clients.filter(created__month=month, created__year=year).count()
        return Response({"all_count": all_count, "per_month": per_month})

    @action(methods=["GET"], detail=False, url_path="profit_graph")
    def profit_graph(self, request):
        year = self.get_report_filters(int, "year")
        resp = []
        for i in range(12):
            profit = self.get_queryset().filter(
                end_time__year=year,
                end_time__month=i + 1,
                provided=True
            ).aggregate(Sum("cost"))["cost__sum"]
            if not profit:
                profit = 0.0
            resp.append(profit)
        return Response(resp, status=status.HTTP_200_OK)
