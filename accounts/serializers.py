# RestFramework
from rest_framework import serializers

# Локальные импорты
from .models import User
from .models import Grade


class UserSerializer(serializers.ModelSerializer):
    approve_email = serializers.ReadOnlyField()
    approve_phone = serializers.ReadOnlyField()
    rating = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "rating",
            "approve_email",
            "approve_phone",
            "auto_confirm"
        ]

    def to_representation(self, instance):
        data = super(UserSerializer, self).to_representation(instance)
        if data["avatar"]:
            if "http://everyservices.itpw.ru" not in data["avatar"]:
                data["avatar"] = "http://everyservices.itpw.ru" + data["avatar"]
        return data


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = "__all__"
