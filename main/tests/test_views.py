import json
from unittest.mock import Mock
from urllib.parse import urljoin

import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ..models import BloodTestResults, Lab, User
from .factories import LabFactory


# Create your tests here.
class SmokeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester")
        self.user2 = User.objects.create_user(username="tester2")
        self.blood_test_result = BloodTestResults.objects.create(
            user=self.user,
            results={
                "values": {
                    "HDL": 87,
                    "LDL": 27,
                    "CHL": 120,
                    "SGR": 73,
                }
            },
        )
        self.blood_test_result2 = BloodTestResults.objects.create(
            user=self.user2,
            results={
                "values": {
                    "HDL": 88,
                    "LDL": 28,
                    "CHL": 121,
                    "SGR": 74,
                }
            },
        )

    def test_blood_test_results(self):
        response = self.client.get(reverse("main:api-results"))
        self.assertEqual(response.status_code, 200)
        c = json.loads(response.content)["data"]
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0]["results"]["values"]["HDL"], 87)


@pytest.mark.django_db
class TestLabViewSet:
    client = APIClient()

    @pytest.mark.parametrize(
        ("country_code", "expected_labs"),
        [
            ("NZ", 1),
            ("GB", 2),
            ("AF", 0),
        ],
    )
    def test_list_multiple_labs_different_country_no_city(
        self, country_code, expected_labs
    ):
        LabFactory(country="NZ")
        LabFactory(country="GB")
        LabFactory(country="GB")

        response = self.client.get(
            reverse(
                "main:api-lab",
                kwargs={
                    "country": f"{country_code}",
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == expected_labs
        assert 3 == Lab.objects.all().count()

    @pytest.mark.parametrize(
        ("country_code", "expected_labs", "city"),
        [
            ("GB", 2, "London"),
            ("GB", 1, "Birmingham"),
            ("GB", 0, "Oxford"),
        ],
    )
    def test_list_multiple_labs_same_country_same_city(
        self, country_code, expected_labs, city
    ):
        LabFactory(country="GB", city="London")
        LabFactory(country="GB", city="London")
        LabFactory(country="GB", city="Birmingham")
        query = f"?city={city}"

        response = self.client.get(
            urljoin(
                reverse(
                    "main:api-lab",
                    kwargs={
                        "country": f"{country_code}",
                    },
                ),
                query,
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == expected_labs
        assert 3 == Lab.objects.all().count()

    @pytest.mark.parametrize(
        ("country_code", "expected_labs", "city"),
        [
            ("CA", 1, "Sydney"),
            ("AU", 1, "Sydney"),
        ],
    )
    def test_list_multiple_labs_different_countries_same_cities(
        self, country_code, expected_labs, city
    ):
        LabFactory(country="CA", city="Sydney")
        LabFactory(country="AU", city="Sydney")
        query = f"?city={city}"

        response = self.client.get(
            urljoin(
                reverse(
                    "main:api-lab",
                    kwargs={
                        "country": f"{country_code}",
                    },
                ),
                query,
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == expected_labs
        assert 2 == Lab.objects.all().count()


@pytest.mark.django_db
class TestGeolocationViewSet:
    client = APIClient()

    @pytest.mark.parametrize(
        ("expected_error_message", "ip_query_param"),
        [
            (
                "Error: query parameter 'ip' was not set. Please pass ip address as a query parameter ",
                "",
            ),
            ("ValueError: {} does not appear to be an IPv4 or IPv6 address", "Invalid"),
        ],
    )
    def test_ip_validation(self, expected_error_message, ip_query_param):
        with pytest.raises(Exception) as err:
            self.client.get(
                urljoin(
                    reverse("main:api-geolocation"), "?ip={}".format(ip_query_param)
                )
            )
        expected_error_message = expected_error_message.format(ip_query_param)
        assert err.value.args[0] == expected_error_message

    @pytest.mark.parametrize(
        ("expected_status_code", "mock_return_value"),
        [
            (status.HTTP_400_BAD_REQUEST, {"wrong": "values"}),
            (status.HTTP_200_OK, {"country_name": "USA", "city": "Rocky Mount"}),
        ],
    )
    def test_geolocation(self, mocker, expected_status_code, mock_return_value):
        mock = Mock()
        mock.json.return_value = mock_return_value
        mocker.patch(
            "main.views.IpGeolocationClient.get_ip_geolocation", return_value=mock
        )

        response = self.client.get(
            urljoin(reverse("main:api-geolocation"), "?ip=192.168.2.10")
        )
        assert response.status_code == expected_status_code
        if expected_status_code == status.HTTP_200_OK:
            data = response.json()
            assert data.get("city") == "Rocky Mount"
            assert data.get("country") == "USA"
