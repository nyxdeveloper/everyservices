# rest framework
from rest_framework import serializers

# локальные импорты
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    duration = serializers.TimeField()
    cost = serializers.FloatField()

    class Meta:
        model = Service
        fields = "__all__"
