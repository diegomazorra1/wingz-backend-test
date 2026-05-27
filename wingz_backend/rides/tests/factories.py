from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory

from wingz_backend.rides.models import Ride
from wingz_backend.users.tests.factories import UserFactory


class RideFactory(DjangoModelFactory[Ride]):
    passenger = SubFactory(UserFactory)
    pickup_address = Faker("street_address")
    dropoff_address = Faker("street_address")

    class Meta:
        model = Ride
