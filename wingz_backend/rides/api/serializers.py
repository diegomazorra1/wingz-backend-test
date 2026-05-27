from rest_framework import serializers

from wingz_backend.rides.models import Ride


class RideSerializer(serializers.ModelSerializer[Ride]):
    class Meta:
        model = Ride
        fields = [
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
        read_only_fields = [
            "id",
            "pickup_address",
            "dropoff_address",
            "created_at",
            "updated_at",
            "url",
        ]
        extra_kwargs = {
            "url": {"view_name": "api:ride-detail", "lookup_field": "pk"},
        }
