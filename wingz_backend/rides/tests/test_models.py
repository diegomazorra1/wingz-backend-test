import pytest

from wingz_backend.rides.models import Ride


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
