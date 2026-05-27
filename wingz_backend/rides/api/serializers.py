from django.contrib.gis.geos import Point
from rest_framework import serializers

from wingz_backend.rides.models import Ride
from wingz_backend.rides.models import RideEvent
from wingz_backend.rides.services import record_ride_created
from wingz_backend.rides.services import record_ride_status_changed
from wingz_backend.rides.services import validate_ride_status_transition


class RideEventSerializer(serializers.ModelSerializer[RideEvent]):
    class Meta:
        model = RideEvent
        fields = [
            "id",
            "description",
            "created_at",
        ]
        read_only_fields = fields


class RideSerializer(serializers.ModelSerializer[Ride]):
    todays_ride_events = serializers.SerializerMethodField()

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
            "todays_ride_events",
            "created_at",
            "updated_at",
            "url",
        ]
        read_only_fields = [
            "id",
            "pickup_address",
            "dropoff_address",
            "todays_ride_events",
            "created_at",
            "updated_at",
            "url",
        ]
        extra_kwargs = {
            "url": {"view_name": "api:ride-detail", "lookup_field": "pk"},
        }

    def create(self, validated_data):
        self._set_pickup_location(validated_data)
        ride = super().create(validated_data)
        record_ride_created(ride)
        return ride

    def update(self, instance, validated_data):
        previous_status = instance.status
        validate_ride_status_transition(previous_status, validated_data.get("status"))
        self._set_pickup_location(validated_data, instance)
        ride = super().update(instance, validated_data)

        if previous_status != ride.status:
            record_ride_status_changed(ride)

        return ride

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

    def get_todays_ride_events(self, ride):
        todays_events = getattr(ride, "todays_ride_events", [])
        return RideEventSerializer(todays_events, many=True).data

    def validate(self, attrs):
        pickup_latitude = attrs.get(
            "pickup_latitude",
            getattr(self.instance, "pickup_latitude", None),
        )
        pickup_longitude = attrs.get(
            "pickup_longitude",
            getattr(self.instance, "pickup_longitude", None),
        )
        dropoff_latitude = attrs.get(
            "dropoff_latitude",
            getattr(self.instance, "dropoff_latitude", None),
        )
        dropoff_longitude = attrs.get(
            "dropoff_longitude",
            getattr(self.instance, "dropoff_longitude", None),
        )

        errors = {}

        if pickup_latitude is None and pickup_longitude is not None:
            errors["pickup_latitude"] = (
                "pickup_latitude is required with pickup_longitude."
            )

        if pickup_longitude is None and pickup_latitude is not None:
            errors["pickup_longitude"] = (
                "pickup_longitude is required with pickup_latitude."
            )

        if dropoff_latitude is None and dropoff_longitude is not None:
            errors["dropoff_latitude"] = (
                "dropoff_latitude is required with dropoff_longitude."
            )

        if dropoff_longitude is None and dropoff_latitude is not None:
            errors["dropoff_longitude"] = (
                "dropoff_longitude is required with dropoff_latitude."
            )

        if errors:
            raise serializers.ValidationError(errors)

        return super().validate(attrs)
