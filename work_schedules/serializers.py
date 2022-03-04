# rest framework
from rest_framework import serializers

# локальные импорты
from .models import SpecialSchedule
from .models import Schedule
from .services import check_schedule_data, check_special_schedule_data


class SpecialScheduleSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    date = serializers.DateField(input_formats=["%d.%m.%Y"], format="%d.%m.%Y")

    class Meta:
        model = SpecialSchedule
        fields = "__all__"

    def create(self, validated_data):
        check_special_schedule_data(validated_data)
        return super(SpecialScheduleSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        check_special_schedule_data(validated_data)
        return super(SpecialScheduleSerializer, self).update(instance, validated_data)


class ScheduleSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    start = serializers.DateField(input_formats=["%d.%m.%Y"], format="%d.%m.%Y")

    class Meta:
        model = Schedule
        fields = "__all__"

    def create(self, validated_data):
        check_schedule_data(validated_data)
        return super(ScheduleSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        check_schedule_data(validated_data)
        return super(ScheduleSerializer, self).update(instance, validated_data)
