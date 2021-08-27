from typing import Any
from typing import Dict

from django.contrib.auth.models import AbstractUser
from django.db import models


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

    class Meta:
        verbose_name_plural = "Blood test results"

    def __str__(self) -> str:
        return self.user.username

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.timestamp,
            "results": self.results,
        }
