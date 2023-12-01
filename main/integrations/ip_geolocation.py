from typing import Dict
from urllib.parse import urljoin

import requests
from django.conf import settings
from requests.models import Response as RequestResponse
from rest_framework import status


def validate_response(
    response: RequestResponse, expected_status: int, method_name: str
):
    if response.status_code == expected_status:
        return

    raise Exception(
        f"IpGeolocationClient {method_name} error, error code: {response.status_code} error message: {response.reason}",
        response.status_code,
    )


class IpGeolocationClient:
    """
    Client to make requests to Ipgeolocation's API.

    see : https://ipgeolocation.io/documentation.html
    """

    ENDPOINT_GET_GEOLOCATION = "/ipgeo"

    def __init__(
        self,
        base_url=None,
        api_key=None,
    ):
        self.session = requests.Session()
        self.base_url = base_url or settings.IP_GEOLOCATION_BASE_URL
        self.api_key = api_key or settings.IP_GEOLOCATION_API_KEY

    def get_ip_geolocation(self, params: Dict[str, str] = None):
        """Get geolocation via IP Geolocation API which
        provides location information for any IPv4/IPv6 address or domain name"""
        method_name = IpGeolocationClient.get_ip_geolocation.__name__
        if params is None:
            params = dict()
        params["apiKey"] = self.api_key
        response = requests.get(
            urljoin(self.base_url, self.ENDPOINT_GET_GEOLOCATION), params=params
        )
        validate_response(
            response=response,
            expected_status=status.HTTP_200_OK,
            method_name=method_name,
        )
        return response.json()
