import pytest
from django.db.utils import IntegrityError

from .factories import LabFactory


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
