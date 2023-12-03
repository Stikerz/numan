"""The main application's URLs."""
from django.urls import path

from . import viewsets

app_name = "main"
urlpatterns = [
    path(
        "api/results/",
        viewsets.BloodTestResultsViewSet.as_view({"get": "list", "post": "create"}),
        name="api-results",
    ),
    path(
        "api/geolocation/",
        viewsets.GeolocationViewSet.as_view({"get": "list"}),
        name="api-geolocation",
    ),
    path("", viewsets.index, name="index"),
    path(
        "api/lab/<country>/",
        viewsets.LabViewSet.as_view({"get": "list"}),
        name="api-lab",
    ),
]
