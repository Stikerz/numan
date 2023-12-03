import ipaddress
from typing import Dict, List

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .authentication import TokenAuthentication
from .integrations.ip_geolocation import IpGeolocationClient
from .models import BloodTestResults, Lab
from .serializers import (
    BloodTestResultsModelSerializer,
    CreateBloodTestSerializer,
    GeolocationViewSetSerializer,
    LabViewSetSerializer,
)


def validate_ip_address(ip_address: str = None):
    if not ip_address:
        raise Exception(
            "Error: query parameter 'ip' was not set. Please pass ip address as a query parameter "
        )
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        raise Exception(
            f"ValueError: {ip_address} does not appear to be an IPv4 or IPv6 address"
        )


def convert_to_dict(lst: List) -> Dict[str, None]:
    return {key: None for key in lst}


def index(request) -> HttpResponse:
    """The main index view, for prettiness."""
    return render(request, "index.html")


class BloodTestResultsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def list(self, request, **kwargs) -> Response:
        """Return a list of blood test results for the current user."""

        query = BloodTestResults.objects.filter(user=request.user)
        serializer = BloodTestResultsModelSerializer(instance=query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, **kwargs) -> Response:
        """Create BloodTestResults for user"""

        user = request.user
        create_blood_serializer = CreateBloodTestSerializer(data=request.data)
        create_blood_serializer.is_valid(raise_exception=True)
        valid_data = create_blood_serializer.validated_data

        lab = get_object_or_404(Lab, pk=valid_data.get("lab"))
        data = {
            "results": convert_to_dict(valid_data.get("blood_test")),
            "user": user,
            "lab": lab,
        }
        instance = BloodTestResults.objects.create(**data)
        blood_test_model_serializer = BloodTestResultsModelSerializer(instance=instance)
        return Response(blood_test_model_serializer.data, status=status.HTTP_200_OK)


class LabViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def list(self, request, **kwargs):
        filters = {"country": kwargs.get("country")}
        city = self.request.query_params.get("city")
        if city:
            filters["city"] = city
        queryset = Lab.objects.filter(**filters)
        serializer = LabViewSetSerializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GeolocationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def list(self, request, **kwargs) -> Response:
        """Perform geolocation on a given IP address."""
        ip = self.request.query_params.get("ip")
        validate_ip_address(ip)

        query_params = {"ip": ip, "fields": "city,country_name"}
        response = IpGeolocationClient().get_ip_geolocation(params=query_params)
        data = response.json()
        serializer = GeolocationViewSetSerializer(
            data={"country": data.get("country_name"), "city": data.get("city")}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
