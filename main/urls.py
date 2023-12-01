"""The main application's URLs."""
from django.urls import path

from . import views

app_name = "main"
urlpatterns = [
    path("api/results/", views.APITestResults.as_view(), name="api-results"),
    path(
        "api/geolocation/",
        views.GeolocationViewSet.as_view({"get": "list"}),
        name="api-geolocation",
    ),
    path("", views.index, name="index"),
    path(
        "api/lab/<country>/",
        views.LabViewSet.as_view({"get": "list"}),
        name="api-lab",
    ),
]
