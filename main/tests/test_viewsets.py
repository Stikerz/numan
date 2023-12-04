import json
from urllib.parse import urljoin

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient

from ..models import BloodTestResults, CustomToken, Lab
from .factories import BloodTestResultsFactory, LabFactory, UserFactory


@pytest.fixture()
def user() -> UserFactory:
    return UserFactory()


@pytest.fixture()
def client() -> APIClient:
    return APIClient()


@pytest.fixture()
def lab() -> LabFactory:
    return LabFactory()


def create_blood_test_results(**kwargs):
    return BloodTestResultsFactory(**kwargs)


def create_token(**kwargs):
    key = get_random_string(length=32)
    return CustomToken.objects.create(key=key, **kwargs)


@pytest.mark.django_db
class TestBloodTestResultsViewSet:
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
        self, results, expected_results, expected_status_code, user, client
    ):
        create_blood_test_results(results=results, user=user)

        client.force_authenticate(user=user)
        response = client.get(reverse("main:api-results"))
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
        self, test_types, expected_results, expected_status_code, user, lab, client
    ):
        assert BloodTestResults.objects.filter(user=user).count() == 0
        data = {"lab": lab.pk, "blood_test": test_types}
        client.force_authenticate(user=user)
        response = client.post(
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

    def test_create_blood_test_results_invalid_lab_404(self, user, client):
        data = {"lab": 4, "blood_test": ["HDL", "LDL", "CBC"]}
        client.force_authenticate(user=user)
        response = client.post(
            reverse("main:api-results"),
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_blood_test_results_viewset_auth(self, client, user):
        token = create_token(user=user, name="token1")
        client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = client.get(reverse("main:api-results"))
        data = response.json()
        assert data == []
        assert response.status_code == status.HTTP_200_OK

    def test_blood_test_results_viewset_no_auth(self, client):
        client.credentials(HTTP_AUTHORIZATION="Token invalidtoken")
        response = client.get(reverse("main:api-results"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLabViewSet:
    @pytest.mark.parametrize(
        ("country_code", "expected_labs"),
        [
            ("NZ", 1),
            ("GB", 2),
            ("AF", 0),
        ],
    )
    def test_list_multiple_labs_different_country_no_city(
        self, country_code, expected_labs, client, user
    ):
        LabFactory(country="NZ")
        LabFactory(country="GB")
        LabFactory(country="GB")

        client.force_authenticate(user=user)
        response = client.get(
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
        self, country_code, expected_labs, city, client, user
    ):
        LabFactory(country="GB", city="London")
        LabFactory(country="GB", city="London")
        LabFactory(country="GB", city="Birmingham")
        query = f"?city={city}"

        client.force_authenticate(user=user)
        response = client.get(
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
        self, country_code, expected_labs, city, client, user
    ):
        LabFactory(country="CA", city="Sydney")
        LabFactory(country="AU", city="Sydney")
        query = f"?city={city}"

        client.force_authenticate(user=user)
        response = client.get(
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

    def test_lab_viewset_auth(self, client, user):
        token = create_token(user=user, name="token1")
        client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = client.get(
            reverse(
                "main:api-lab",
                kwargs={
                    "country": "GB",
                },
            )
        )
        data = response.json()
        assert data == []
        assert response.status_code == status.HTTP_200_OK

    def test_lab_viewset_no_auth(self, client):
        client.credentials(HTTP_AUTHORIZATION="Token invalidtoken")
        response = client.get(reverse("main:api-lab", kwargs={"country": "GB"}))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGeolocationViewSet:
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
    def test_ip_validation(self, expected_error_message, ip_query_param, user, client):
        client.force_authenticate(user=user)

        with pytest.raises(Exception) as err:
            client.get(
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
    def test_geolocation(
        self, mocker, expected_status_code, mock_return_value, client, user
    ):
        mocker.patch(
            "main.viewsets.IpGeolocationClient.get_ip_geolocation",
            return_value=mock_return_value,
        )
        client.force_authenticate(user=user)
        response = client.get(
            urljoin(reverse("main:api-geolocation"), "?ip=192.168.2.10")
        )
        assert response.status_code == expected_status_code
        if expected_status_code == status.HTTP_200_OK:
            data = response.json()
            assert data.get("city") == "Rocky Mount"
            assert data.get("country") == "USA"

    def test_geolocation_viewset_auth(self, mocker, client, user):
        mocker.patch(
            "main.viewsets.IpGeolocationClient.get_ip_geolocation",
            return_value={"country_name": "USA", "city": "Rocky Mount"},
        )
        token = create_token(user=user, name="token1")
        client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = client.get(
            urljoin(reverse("main:api-geolocation"), "?ip=192.168.2.10")
        )
        data = response.json()
        assert data == {"country": "USA", "city": "Rocky Mount"}
        assert response.status_code == status.HTTP_200_OK

    def test_geolocation_viewset_no_auth(self, client):
        client.credentials(HTTP_AUTHORIZATION="Token invalidtoken")
        response = client.get(reverse("main:api-geolocation"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
