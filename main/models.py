from typing import Any, Dict

from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.db import models
from django_countries.fields import CountryField


class User(AbstractUser):
    """The user."""

    pass


class BloodTestResults(models.Model):
    """A blood test the user ordered, possibly carrying results from the lab."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time this result was created.",
    )
    results = models.JSONField(
        default=dict,
        blank=True,
        help_text="The results we got back from the lab.",
    )
    ready = models.BooleanField(
        default=False,
        help_text="Whether the results have come back from the lab yet.",
    )

    lab = models.ForeignKey(
        "Lab",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        verbose_name_plural = "Blood test results"

    def __str__(self) -> str:
        return self.user.username

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.timestamp,
            "results": self.results,
        }


class Lab(models.Model):
    """Laboratory which run blood tests."""

    name = models.CharField(max_length=128, unique=True)
    address = models.CharField(max_length=256)
    address_2 = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=256)
    post_code = models.CharField(max_length=8)
    country = CountryField(default="GB", blank_label="(select country)")
    email = models.CharField(max_length=254, validators=[EmailValidator()])
    number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

    @property
    def country_name(self) -> str:
        return self.country.name
