import pytest
from django.core.exceptions import MultipleObjectsReturned
from django.db.utils import IntegrityError
from django.utils.crypto import get_random_string

from main.models import CustomToken

from .factories import LabFactory, UserFactory


@pytest.mark.django_db
class TestLabModel:
    def test_unique_name_constraint(self):
        LabFactory(name="Lab Alpha")
        with pytest.raises(IntegrityError):
            LabFactory(name="Lab Alpha")

    @pytest.mark.parametrize(
        ("country_code", "country_name"),
        [
            ("NZ", "New Zealand"),
            ("GB", "United Kingdom"),
            ("AF", "Afghanistan"),
        ],
    )
    def test_country_property(self, country_code, country_name):
        lab = LabFactory(country=country_code)
        assert lab.country.name == country_name


@pytest.mark.django_db
class TestCustomTokenModel:
    def test_multiple_token_one_user(self):
        user = UserFactory()

        CustomToken.objects.create(
            user=user,
            key=get_random_string(length=32),
            name=get_random_string(length=8),
        )
        CustomToken.objects.create(
            user=user,
            key=get_random_string(length=32),
            name=get_random_string(length=8),
        )
        CustomToken.objects.create(
            user=user,
            key=get_random_string(length=32),
            name=get_random_string(length=8),
        )

        with pytest.raises(MultipleObjectsReturned):
            CustomToken.objects.get(user=user)
