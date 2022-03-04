# rest framework
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

# django
import datetime
from django.db import transaction

from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.utils import timezone
from django.views import View
# rest framework
from rest_framework.response import Response

# импорты приложений
from records.models import Record
from accounts.models import User
from accounts.models import Grade
from clients.models import Client
from accounts.serializers import GradeSerializer
from accounts.serializers import UserSerializer
from records.serializers import CreateRecordFromLandingSerializer

# импорты проекта
from everyservices.services import clean_phone
from records.exception import DayOffException

from records.services import get_free_times
from services.models import Service
from services.serializers import ServiceSerializer
from .exceptions import MasterIdRequired


class PortfolioView(View):

    def post(self, request, pk):
        try:
            master = User.objects.get(pk=pk)
            name = request.POST["name"]
            phone = request.POST["phone"]
            phone = clean_phone(phone)
            try:
                email = request.POST["email"]
            except KeyError:
                email = ""
            service = Service.objects.get(id=int(request.POST["service"]))
            date = request.POST["date"]
            y, m, d = date.split("-")
            date = f"{d}.{m}.{y}"
            time = request.POST["time"]
            recording = datetime.datetime.strptime(f"{date} {time}", "%d.%m.%Y %H:%M")

            try:
                client = Client.objects.get(phone=phone)
            except Client.DoesNotExist:
                client = Client.objects.create(name=name, phone=phone, email=email)
            Record.objects.create(
                user=master,
                client=client,
                service=service,
                cost=service.cost,
                duration=service.duration,
                recording_time=recording
            )



        except (User.DoesNotExist, ValidationError):
            return render(request, "master_not_found.html", status=404)
        return render(request, "succes_record.html", context={
            "master": master
        })

    def get(self, request, pk):
        try:
            master = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValidationError):
            return render(request, "master_not_found.html", status=404)
        return render(request, "masters-landing.html", context={
            "master": master,
            "rating": str(master.rating)
        })


class SendGradeView(View):
    def post(self, request, pk):
        try:
            master = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValidationError):
            return render(request, "master_not_found.html", status=404)
        name = request.POST["name"]
        phone = request.POST["phone"]
        phone = clean_phone(phone)
        grade = request.POST["rating"]
        try:
            comment = request.POST["grade-text"]
        except KeyError:
            comment = ""

        if master.records.filter(client__phone=phone, was_rated=False).exists():
            record = master.records.filter(client__phone=phone, was_rated=False).first()
            record.was_rated = True
            record.save()
            Grade.objects.create(
                grade=int(grade),
                assessed=master,
                client=name,
                comment=comment
            )
        else:
            return render(request, "grade_failed.html", context={
                "master": master
            })
        return render(request, "success_grade.html", context={
            "master": master
        })


class PrivacyView(View):
    def get(self, request):
        return render(request, "privacy.html")


class TimeView(View):
    def get(self, request, service, date):
        try:
            service = Service.objects.get(pk=service)
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            if date < timezone.now().date():
                return render(request, "invalid-date.html")
            return render(request, "free-times.html", context={
                "times": get_free_times(service.user, date, service.duration)
            })
        except Service.DoesNotExist:
            return Response({"detail": "Услуга не найдена"}, status=404)
        except DayOffException:
            return render(request, "day-off.html")


class PortfolioViewSet(GenericViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_master_id(self):
        if self.request.query_params.get("mst") is not None and self.request.query_params.get("mst") != "":
            return self.request.query_params.get("mst")
        raise MasterIdRequired

    @action(methods=["GET"], detail=False)
    def services(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(user_id=self.get_master_id())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @action(methods=["GET"], detail=False)
    def grades(self, request):
        queryset = Grade.objects.filter(assessed_id=self.get_master_id())
        serializer = GradeSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @action(methods=["POST"], detail=False)
    def send_grade(self, request):
        phone = request.data.get("phone")
        phone = clean_phone(phone)
        name = request.data.get("name")
        grade = request.data.get("grade")
        assessed = request.data.get("assessed")
        comment = request.data.get("comment")

        try:
            master = User.objects.get(is_active=True, id=assessed)
        except User.DoesNotExist:
            return Response({"detail": "Мастер не найден"}, status=404)

        if master.records.filter(client__phone=phone, was_rated=False).exists():
            record = master.records.filter(client__phone=phone, was_rated=False).first()
            record.was_rated = True
            record.save()
            Grade.objects.create(
                grade=int(grade),
                assessed=master,
                client=name if name else "Аноним",
                comment=comment if comment else ''
            )
        else:
            return Response({
                "detail": "Мы не нашли вас в числе последних клиентов мастера. Чтобы оставить отзыв, сделайте как минимум одну запись"},
                status=403)

        # serializer = GradeSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        # return Response(serializer.data, status=201)
        return Response({"detail": "Спасибо за отзыв"}, status=200)

    @transaction.atomic
    @action(methods=["POST"], detail=False)
    def create_record(self, request):
        serializer = CreateRecordFromLandingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        try:
            service = Service.objects.get(id=data["service"])
            if service.user.clients.filter(phone=clean_phone(data["phone"])).exists():
                client = service.user.clients.get(phone=clean_phone(data["phone"]))
            else:
                client = service.user.clients.create(name=data["name"], phone=clean_phone(data["phone"]))
            recording_time = datetime.datetime.strptime(f"{data['date']} {data['time']}", "%d.%m.%Y %H:%M")
            service.user.records.create(
                service=service, client=client, cost=service.cost, duration=service.duration, comment=data["comment"],
                recording_time=recording_time
            )
        except Service.DoesNotExist:
            return Response({"detail": "Услуга не существует"}, status=404)
        return Response({"detail": "Запись успешно оформлена"}, status=201)

    @action(methods=["GET"], detail=False)
    def master(self, request):
        queryset = User.objects.filter(id=self.get_master_id())
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @action(methods=["GET"], detail=False)
    def free_time(self, request):
        try:
            service = Service.objects.get(pk=request.query_params.get("sv"))
            # date = datetime.datetime.strptime(request.query_params.get("d"), "%Y-%m-%d").date()
            date = datetime.datetime.strptime(request.query_params.get("d"), "%d.%m.%Y").date()
            if date < timezone.now().date():
                return Response({"detail": "Невалидная дата"}, status=400)
            ft = get_free_times(service.user, date, service.duration)
            return Response({"times": [i.strftime("%H:%M") for i in ft]})
        except Service.DoesNotExist:
            return Response({"detail": "Услуга не найдена"}, status=404)
        except DayOffException:
            return Response({"detail": "Мастер не работает в этот день"}, status=400)
