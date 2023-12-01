from contextlib import nullcontext as does_not_raise
from unittest.mock import Mock

import pytest
from django.test import override_settings
from rest_framework import status

from main.integrations.ip_geolocation import IpGeolocationClient


def successful_ip_geolocation_response():
    return {
        "ip": "8.8.8.8",
        "city": "Mountain View",
        "country_name": "United States",
        "country_name_official": "United States of America",
    }


class TestIpGeolocationClientClient:
    @pytest.mark.parametrize(
        [
            "api_key",
            "base_url",
            "expected_url",
            "expected_api_key",
        ],
        [
            (None, None, "https://fakeipgeolocation.com/api", "iamaapisecret"),
            (
                "therealapikey",
                "https://fooboo.com/",
                "https://fooboo.com/",
                "therealapikey",
            ),
        ],
    )
    def test_params(
        self,
        api_key,
        base_url,
        expected_url,
        expected_api_key,
    ):
        with override_settings(
            IP_GEOLOCATION_API_KEY="iamaapisecret",
            IP_GEOLOCATION_BASE_URL="https://fakeipgeolocation.com/api",
        ):
            client = IpGeolocationClient(
                base_url=base_url,
                api_key=expected_api_key,
            )
            assert client.base_url == expected_url
            assert client.api_key == expected_api_key

    @pytest.mark.parametrize(
        [
            "response",
            "expected_exception",
            "expected_response",
            "ip",
            "status_code",
            "reason",
        ],
        [
            (
                {"json": {}, "status_code": status.HTTP_400_BAD_REQUEST},
                pytest.raises(Exception),
                None,
                "8.8.8.8",
                status.HTTP_400_BAD_REQUEST,
                "bad request",
            ),
            (
                {
                    "json": successful_ip_geolocation_response(),
                    "status_code": status.HTTP_200_OK,
                },
                does_not_raise(),
                successful_ip_geolocation_response(),
                "8.8.8.8",
                status.HTTP_200_OK,
                "",
            ),
        ],
    )
    def test_get_geolocation(
        self,
        response,
        expected_exception,
        expected_response,
        ip,
        mocker,
        status_code,
        reason,
    ):
        with override_settings(
            IP_GEOLOCATION_API_KEY="fooboo",
            IP_GEOLOCATION_BASE_URL="https://fakeipgeolocation.com",
        ):
            client = IpGeolocationClient()
            mock = Mock()
            mock.status_code = status_code
            mock.json.return_value = response["json"]
            mock.reason = reason
            mocker.patch(
                "main.integrations.ip_geolocation.requests.get", return_value=mock
            )
            param = {"ip": ip}
            with expected_exception:
                resp = client.get_ip_geolocation(param)
                assert resp == expected_response
