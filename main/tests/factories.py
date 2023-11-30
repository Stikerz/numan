import factory
from factory.django import DjangoModelFactory

from main import models


class LabFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"lab_name_{n}")
    address = "1 Lab Street"
    address_2 = ""
    city = "London"
    post_code = "SW1 9RH"
    country = "GB"
    email = factory.Sequence(lambda n: f"lab_{n}@example.com")
    number = "0795033954"

    class Meta:
        model = models.Lab
