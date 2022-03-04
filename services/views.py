# rest framework
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter

# локальные импорты
from .models import Service
from .serializers import ServiceSerializer

# импорты проекта
from everyservices.pagination import StandardResultsSetPagination
from everyservices.mixins import ModelOptionFieldsMixin


class ServiceViewSet(ModelViewSet, ModelOptionFieldsMixin):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter, ]
    search_fields = ["name", "cost", "duration", "description"]
    ordering_fields = search_fields
    opt = ["id", "name"]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
