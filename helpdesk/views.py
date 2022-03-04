# rest framework
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

# django
from django.db.models import Q

# локальные импорты
from .models import HelpdeskMessage
from .serializers import HelpdeskMessageSerializer

# импорты проекта
from everyservices.pagination import StandardResultsSetPagination


class HelpdeskMessageViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    queryset = HelpdeskMessage.objects.all()
    serializer_class = HelpdeskMessageSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["text"]

    def get_queryset(self):
        return self.queryset.filter(Q(to=self.request.user) | Q(user=self.request.user)).distinct()

    def list(self, request, *args, **kwargs):
        # читаем все сообщения, которые запрашивает пользователь
        self.filter_queryset(self.get_queryset()).filter(to=self.request.user).update(read=True)
        return super(HelpdeskMessageViewSet, self).list(request, *args, **kwargs)
