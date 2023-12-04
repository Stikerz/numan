import ipaddress
from typing import Any, Dict, List

from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import View
from rest_framework import status, viewsets
from rest_framework.response import Response

from .integrations.ip_geolocation import IpGeolocationClient
from .models import BloodTestResults, Lab
from .serializers import GeolocationSerializer, LabSerializer


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


class APIClass(View):
    """A parent class that makes it easier to write API views."""

    def dispatch(self, request, *args, **kwargs) -> JsonResponse:
        """Dispatch the request."""
        # Assume that this user is the one we're authenticating as.
        request.user = get_user_model().objects.all()[0]

        # Route the request through the method.
        response = super().dispatch(request, *args, **kwargs)

        # If the response includes an error, set the proper status codes.
        if "error" in response:
            return JsonResponse(response, status=422)
        else:
            return JsonResponse({"data": response})


class APITestResults(APIClass):
    def get(self, request) -> List[Dict[str, Any]]:
        """Return a list of blood test results for the current user."""
        return [
            btr.to_dict() for btr in BloodTestResults.objects.filter(user=request.user)
        ]


def index(request) -> HttpResponse:
    """The main index view, for prettiness."""
    return render(request, "index.html")


class LabViewSet(viewsets.ViewSet):
    serializer_class = LabSerializer

    def list(self, request, **kwargs):
        filters = {"country": kwargs.get("country").upper()}
        city = self.request.query_params.get("city")
        if city:
            filters["city__iexact"] = city
        queryset = Lab.objects.filter(**filters)
        serializer = LabSerializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GeolocationViewSet(viewsets.ViewSet):
    serializer_class = GeolocationSerializer

    def list(self, request, **kwargs) -> Response:
        """Perform geolocation on a given IP address."""
        ip = self.request.query_params.get("ip")
        validate_ip_address(ip)

        query_params = {"ip": ip, "fields": "city,country_name"}
        response = IpGeolocationClient().get_ip_geolocation(params=query_params)
        data = response.json()
        serializer = GeolocationSerializer(
            data={"country": data.get("country_name"), "city": data.get("city")}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
