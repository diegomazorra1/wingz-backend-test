from wingz_backend.rides.api.serializers import RideSerializer
from wingz_backend.rides.models import Ride


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
