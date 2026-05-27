from django.contrib.gis.geos import Point
from rest_framework import serializers

from wingz_backend.rides.api.errors import InvalidRideStatusTransition
from wingz_backend.rides.models import Ride
from wingz_backend.rides.models import RideEvent


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
        RideEvent.objects.create(ride=ride, description="Ride created")
        return ride

    def update(self, instance, validated_data):
        previous_status = instance.status
        self._validate_status_transition(previous_status, validated_data.get("status"))
        self._set_pickup_location(validated_data, instance)
        ride = super().update(instance, validated_data)

        if previous_status != ride.status:
            RideEvent.objects.create(
                ride=ride,
                description=f"Status changed to {ride.status}",
            )

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
        self._validate_coordinate_pair(
            attrs,
            latitude_field="pickup_latitude",
            longitude_field="pickup_longitude",
        )
        self._validate_coordinate_pair(
            attrs,
            latitude_field="dropoff_latitude",
            longitude_field="dropoff_longitude",
        )

        return super().validate(attrs)

    def _validate_coordinate_pair(self, attrs, *, latitude_field, longitude_field):
        latitude = self._get_effective_value(attrs, latitude_field)
        longitude = self._get_effective_value(attrs, longitude_field)

        if latitude is None and longitude is not None:
            msg = f"{latitude_field} is required with {longitude_field}."
            raise serializers.ValidationError(
                {latitude_field: msg},
            )

        if longitude is None and latitude is not None:
            msg = f"{longitude_field} is required with {latitude_field}."
            raise serializers.ValidationError(
                {longitude_field: msg},
            )

    def _get_effective_value(self, attrs, field):
        if field in attrs:
            return attrs[field]

        return getattr(self.instance, field, None)

    def _validate_status_transition(self, previous_status, requested_status):
        terminal_statuses = {Ride.Status.CANCELED, Ride.Status.COMPLETED}
        if (
            requested_status
            and requested_status != previous_status
            and previous_status in terminal_statuses
        ):
            raise InvalidRideStatusTransition(previous_status, requested_status)
