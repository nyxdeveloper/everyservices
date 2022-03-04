# rest framework
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

# сторонние зависимости
from django_filters.rest_framework import DjangoFilterBackend

# импорты проекта
from everyservices.pagination import StandardResultsSetPagination
from everyservices.mixins import ModelOptionFieldsMixin

# локальные импорты
from .models import Client
from .serializers import ClientContactSerializer


class ClientContactViewSet(ModelViewSet, ModelOptionFieldsMixin):
    queryset = Client.objects.all()
    serializer_class = ClientContactSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]
    filterset_fields = ["blacklist", "created"]
    search_fields = ["name", "phone", "email", "comment", "blacklist_comment"]
    ordering_fields = ["service", "client", "cost", "duration", "recording_time"]
    pagination_class = StandardResultsSetPagination
    opt = ["id", "name"]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(methods=["POST"], detail=False, url_path="bl")
    def change_blacklist_status(self, request):
        bl = request.data.get("blacklist")
        c = request.data.get("comment")
        try:
            client = self.get_queryset().get(id=request.data.get("client"))
            client.blacklist = bl
            client.blacklist_comment = c if c else ""
            client.save()
            if bl:
                return Response({"detail": f"{client.name} был добавлен в черный список"}, status=status.HTTP_200_OK)
            return Response({"detail": f"{client.name} был удален из черного списка"}, status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response({"detail": "Клиент не найден"}, status=status.HTTP_404_NOT_FOUND)
