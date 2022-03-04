# rest framework
from rest_framework import serializers

# локальные импорты
from .models import Client


class ClientContactSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    blacklist = serializers.ReadOnlyField()
    created = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = Client
        fields = "__all__"
