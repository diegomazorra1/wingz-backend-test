from django.contrib.gis.geos import Point
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

    def create(self, validated_data):
        self._set_pickup_location(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._set_pickup_location(validated_data, instance)
        return super().update(instance, validated_data)

    def _set_pickup_location(self, validated_data, instance=None):
        latitude = validated_data.get(
            "pickup_latitude",
            getattr(instance, "pickup_latitude", None),
        )
        longitude = validated_data.get(
            "pickup_longitude",
            getattr(instance, "pickup_longitude", None),
        )

        if latitude is None or longitude is None:
            return

        validated_data["pickup_location"] = Point(
            float(longitude),
            float(latitude),
            srid=4326,
        )
