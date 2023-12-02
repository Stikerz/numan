from rest_framework import serializers

from main.constants.blood_tests import BLOOD_TEST_CHOICES
from main.models import BloodTestResults


class LabViewSetSerializer(serializers.Serializer):
    name = serializers.CharField()
    address = serializers.CharField()
    address_2 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField()
    post_code = serializers.CharField()
    country = serializers.CharField()
    email = serializers.CharField()
    number = serializers.CharField()


class GeolocationViewSetSerializer(serializers.Serializer):
    country = serializers.CharField()
    city = serializers.CharField()


class CreateBloodTestSerializer(serializers.Serializer):
    lab = serializers.IntegerField()
    blood_test = serializers.MultipleChoiceField(choices=BLOOD_TEST_CHOICES)


class BloodTestResultsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodTestResults
        fields = "__all__"
