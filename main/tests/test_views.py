import json
from unittest.mock import Mock
from urllib.parse import urljoin

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ..models import BloodTestResults, Lab
from .factories import BloodTestResultsFactory, LabFactory, UserFactory


@pytest.fixture()
def user() -> UserFactory:
    return UserFactory()


@pytest.fixture()
def lab() -> LabFactory:
    return LabFactory()


def create_blood_test_results(**kwargs):
    return BloodTestResultsFactory(**kwargs)


@pytest.mark.django_db
class TestBloodTestResultsViewSet:
    client = APIClient()

    @pytest.mark.parametrize(
        ("results", "expected_status_code", "expected_results"),
        [
            (
                {
                    "HDL": 87,
                    "LDL": 27,
                    "CBC": 120,
                },
                status.HTTP_200_OK,
                {
                    "HDL": 87,
                    "LDL": 27,
                    "CBC": 120,
                },
            ),
            (
                {
                    "HDL": 88,
                    "LDL": 28,
                    "CBC": 121,
                },
                status.HTTP_200_OK,
                {
                    "HDL": 88,
                    "LDL": 28,
                    "CBC": 121,
                },
            ),
        ],
    )
    def test_list_blood_test_results(
        self, results, expected_results, expected_status_code, user
    ):
        create_blood_test_results(results=results, user=user)

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("main:api-results"))
        data = response.json()

        assert response.status_code == expected_status_code
        assert data[0].get("results") == expected_results
        assert data[0].get("user") == user.pk
        assert len(data) == 1
        assert BloodTestResults.objects.filter(user=user).count() == 1

    @pytest.mark.parametrize(
        ("test_types", "expected_status_code", "expected_results"),
        [
            (
                ["HDL", "LDL", "CBC"],
                status.HTTP_200_OK,
                {
                    "HDL": None,
                    "LDL": None,
                    "CBC": None,
                },
            ),
            (
                ["HDL"],
                status.HTTP_200_OK,
                {
                    "HDL": None,
                },
            ),
            (["UNSUPPORTED_TEST"], status.HTTP_400_BAD_REQUEST, None),
        ],
    )
    def test_create_blood_test_results(
        self, test_types, expected_results, expected_status_code, user, lab
    ):
        assert BloodTestResults.objects.filter(user=user).count() == 0
        data = {"lab": lab.pk, "blood_test": test_types}
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse("main:api-results"),
            data=json.dumps(data),
            content_type="application/json",
        )
        data = response.json()

        assert response.status_code == expected_status_code
        if response.status_code == status.HTTP_200_OK:
            assert data.get("results") == expected_results
            assert data.get("user") == user.pk
            assert data.get("lab") == lab.pk
            assert BloodTestResults.objects.filter(user=user).count() == 1

    def test_create_blood_test_results_invalid_lab_404(self):
        data = {"lab": 4, "blood_test": ["HDL", "LDL", "CBC"]}
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse("main:api-results"),
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


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
