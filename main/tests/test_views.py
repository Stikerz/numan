import json
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

    def test_geolocation(self):
        response = self.client.get(
            reverse("main:api-geolocation"), {"ip": "174.19.29.182"}
        )
        self.assertEqual(response.status_code, 200)
        c = json.loads(response.content)["data"]
        self.assertEqual(c["city"], "Rocky Mount")
        self.assertEqual(c["country"], "USA")

    def test_blood_test_results(self):
        response = self.client.get(reverse("main:api-results"))
        self.assertEqual(response.status_code, 200)
        c = json.loads(response.content)["data"]
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0]["results"]["values"]["HDL"], 87)


@pytest.mark.django_db
class TestLabViewset:
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
