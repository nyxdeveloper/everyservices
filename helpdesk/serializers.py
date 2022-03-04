# rest framework
from rest_framework import serializers

# локальные импорты
from .models import HelpdeskMessage

# импорты приложений
from accounts.models import User


class HelpdeskMessageSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(), queryset=User.objects.all())

    class Meta:
        model = HelpdeskMessage
        fields = "__all__"
