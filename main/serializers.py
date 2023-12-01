from rest_framework import serializers


class LabSerializer(serializers.Serializer):
    name = serializers.CharField()
    address = serializers.CharField()
    address_2 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField()
    post_code = serializers.CharField()
    country = serializers.CharField()
    email = serializers.CharField()
    number = serializers.CharField()


class GeolocationSerializer(serializers.Serializer):
    country = serializers.CharField()
    city = serializers.CharField()
