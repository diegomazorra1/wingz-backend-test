import pytest

from wingz_backend.rides.models import Ride
from wingz_backend.rides.models import RideEvent
from wingz_backend.rides.tests.factories import RideEventFactory


@pytest.mark.django_db
def test_ride_defaults_to_requested_status(user):
    ride = Ride.objects.create(
        passenger=user,
        pickup_address="123 Main St",
        dropoff_address="456 Market St",
    )

    assert ride.status == Ride.Status.REQUESTED


@pytest.mark.django_db
def test_ride_string_representation(user):
    ride = Ride.objects.create(
        passenger=user,
        pickup_address="123 Main St",
        dropoff_address="456 Market St",
    )

    assert str(ride) == f"Ride #{ride.pk} - {Ride.Status.REQUESTED}"


@pytest.mark.django_db
def test_ride_event_belongs_to_ride(user):
    ride = Ride.objects.create(passenger=user)
    event = RideEvent.objects.create(
        ride=ride,
        description="Driver accepted the ride.",
    )

    assert list(ride.events.all()) == [event]


@pytest.mark.django_db
def test_ride_event_string_representation():
    event = RideEventFactory.create(description="Driver accepted the ride.")

    assert str(event) == f"Ride #{event.ride_id} - Driver accepted the ride."
