from wingz_backend.rides.api.serializers import RideSerializer
from wingz_backend.rides.models import Ride
from wingz_backend.rides.models import RideEvent
from wingz_backend.rides.tests.factories import RideFactory


def test_ride_serializer_fields():
    assert RideSerializer.Meta.model is Ride
    assert RideSerializer.Meta.fields == [
        "id",
        "passenger",
        "driver",
        "pickup_address",
        "dropoff_address",
        "pickup_latitude",
        "pickup_longitude",
        "dropoff_latitude",
        "dropoff_longitude",
        "scheduled_at",
            "status",
            "fare_amount",
            "notes",
            "todays_ride_events",
            "created_at",
            "updated_at",
            "url",
    ]


def test_ride_serializer_keeps_generated_addresses_read_only(user):
    serializer = RideSerializer(
        data={
            "passenger": user.pk,
            "pickup_address": "Ignored pickup address",
            "dropoff_address": "Ignored dropoff address",
            "pickup_latitude": "37.774900",
            "pickup_longitude": "-122.419400",
            "dropoff_latitude": "37.784900",
            "dropoff_longitude": "-122.409400",
        },
    )

    assert serializer.is_valid(), serializer.errors
    assert "pickup_address" not in serializer.validated_data
    assert "dropoff_address" not in serializer.validated_data


def test_ride_serializer_builds_pickup_location_from_coordinates(user):
    latitude = 37.774900
    longitude = -122.419400
    serializer = RideSerializer(
        data={
            "passenger": user.pk,
            "pickup_latitude": str(latitude),
            "pickup_longitude": str(longitude),
        },
    )

    assert serializer.is_valid(), serializer.errors
    ride = serializer.save()

    assert ride.pickup_location.x == longitude
    assert ride.pickup_location.y == latitude


def test_ride_serializer_creates_ride_event_on_create(user):
    serializer = RideSerializer(
        data={
            "passenger": user.pk,
        },
    )

    assert serializer.is_valid(), serializer.errors
    ride = serializer.save()

    assert RideEvent.objects.filter(
        ride=ride,
        description="Ride created",
    ).exists()


def test_ride_serializer_creates_ride_event_on_status_change(db):
    ride = RideFactory.create(status=Ride.Status.REQUESTED)
    serializer = RideSerializer(
        ride,
        data={"status": Ride.Status.EN_ROUTE},
        partial=True,
    )

    assert serializer.is_valid(), serializer.errors
    serializer.save()

    assert RideEvent.objects.filter(
        ride=ride,
        description=f"Status changed to {Ride.Status.EN_ROUTE}"",
    ).exists()


def test_ride_serializer_does_not_create_event_without_status_change(db):
    ride = RideFactory.create(status=Ride.Status.REQUESTED)
    serializer = RideSerializer(
        ride,
        data={"notes": "Updated notes only."},
        partial=True,
    )

    assert serializer.is_valid(), serializer.errors
    serializer.save()

    assert not RideEvent.objects.filter(ride=ride).exists()
