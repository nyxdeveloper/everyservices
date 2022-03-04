# rest framework
from rest_framework import serializers

# django
from django.db.models import Q

# локальные импорты
from .models import Record


class RecordSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    duration = serializers.TimeField()
    cost = serializers.FloatField()

    end_time = serializers.DateTimeField(read_only=True)

    cancellation_reason = serializers.ReadOnlyField()
    provided = serializers.ReadOnlyField()
    canceled = serializers.ReadOnlyField()
    confirmed = serializers.ReadOnlyField()
    was_rated = serializers.ReadOnlyField()

    class Meta:
        model = Record
        fields = "__all__"


# class RecordPortfolioSerializer(serializers.ModelSerializer):
#     # duration = serializers.TimeField()
#     # cost = serializers.FloatField()
#     #
#     # end_time = serializers.DateTimeField(read_only=True)
#     #
#     # cancellation_reason = serializers.ReadOnlyField()
#     # provided = serializers.ReadOnlyField()
#     # canceled = serializers.ReadOnlyField()
#     # confirmed = serializers.ReadOnlyField()
#     # was_rated = serializers.ReadOnlyField()
#
#     class Meta:
#         model = Record
#         fields = ["service", ""]


class CreateRecordFromLandingSerializer(serializers.Serializer):
    service = serializers.IntegerField(allow_null=False)
    name = serializers.CharField(allow_null=False)
    phone = serializers.CharField(allow_null=False)
    date = serializers.DateField(input_formats=["%d.%m.%Y"])
    time = serializers.TimeField(input_formats=["%H:%M"])
    comment = serializers.CharField(required=False, allow_null=True)
