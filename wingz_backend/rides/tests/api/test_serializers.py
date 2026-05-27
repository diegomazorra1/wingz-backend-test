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
