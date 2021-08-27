import json

from django.test import TestCase
from django.urls import reverse

from .models import BloodTestResults
from .models import User


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
