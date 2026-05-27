from django.contrib.gis.geos import Point
from factory import Faker
from factory import LazyAttribute
from factory import SubFactory
from factory.django import DjangoModelFactory

from wingz_backend.rides.models import Ride
from wingz_backend.users.tests.factories import UserFactory


class RideFactory(DjangoModelFactory[Ride]):
    passenger = SubFactory(UserFactory)
    pickup_address = Faker("street_address")
    dropoff_address = Faker("street_address")
    pickup_latitude = 37.774900
    pickup_longitude = -122.419400
    pickup_location = LazyAttribute(
        lambda ride: Point(
            float(ride.pickup_longitude),
            float(ride.pickup_latitude),
            srid=4326,
        )
        if ride.pickup_latitude is not None and ride.pickup_longitude is not None
        else None,
    )

    class Meta:
        model = Ride
