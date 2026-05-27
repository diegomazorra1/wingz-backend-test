from datetime import timedelta

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Prefetch
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet

from wingz_backend.rides.api.serializers import RideSerializer
from wingz_backend.rides.models import Ride
from wingz_backend.rides.models import RideEvent

SORT_DISTANCE_TO_PICKUP = "distance_to_pickup"
SORT_PICKUP_TIME = "pickup_time"


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="status",
                description="Filter rides by status.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="rider_email",
                description="Filter rides by passenger/rider email.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="sort",
                description=(
                    "Sort rides by pickup_time or distance_to_pickup. "
                    "distance_to_pickup requires latitude and longitude."
                ),
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="latitude",
                description="Current GPS latitude used for distance_to_pickup sorting.",
                required=False,
                type=float,
            ),
            OpenApiParameter(
                name="longitude",
                description=(
                    "Current GPS longitude used for distance_to_pickup sorting."
                ),
                required=False,
                type=float,
            ),
        ],
    ),
)
class RideViewSet(ModelViewSet):
    serializer_class = RideSerializer
    queryset = Ride.objects.select_related("passenger", "driver")
    lookup_field = "pk"

    def get_queryset(self):
        queryset = self._with_last_24_hours_ride_events(super().get_queryset())
        query_params = getattr(self.request, "query_params", self.request.GET)
        status = query_params.get("status")
        rider_email = query_params.get("rider_email")
        sort = query_params.get("sort")

        self._validate_query_params(status, sort)

        if status:
            queryset = queryset.filter(status=status)

        if rider_email:
            queryset = queryset.filter(passenger__email__iexact=rider_email)

        if sort == SORT_PICKUP_TIME:
            queryset = queryset.order_by("scheduled_at", "id")

        if sort == SORT_DISTANCE_TO_PICKUP:
            queryset = self._order_by_distance_to_pickup(queryset, query_params)

        return queryset

    def _validate_query_params(self, status, sort):
        if status and status not in Ride.Status.values:
            raise ValidationError({"status": "Invalid ride status."})

        valid_sort_values = {SORT_PICKUP_TIME, SORT_DISTANCE_TO_PICKUP}
        if sort and sort not in valid_sort_values:
            msg = "Invalid sort option. Use pickup_time or distance_to_pickup."
            raise ValidationError({"sort": msg})

    def _with_last_24_hours_ride_events(self, queryset):
        start = timezone.now() - timedelta(hours=24)
        recent_events = RideEvent.objects.filter(
            created_at__gte=start,
        ).order_by("-created_at", "-id")

        return queryset.prefetch_related(
            Prefetch(
                "events",
                queryset=recent_events,
                to_attr="todays_ride_events",
            ),
        )

    def _order_by_distance_to_pickup(self, queryset, query_params):
        latitude = self._get_float_query_param(query_params, "latitude")
        longitude = self._get_float_query_param(query_params, "longitude")
        user_location = Point(longitude, latitude, srid=4326)

        return (
            queryset.filter(pickup_location__isnull=False)
            .annotate(distance_to_pickup=Distance("pickup_location", user_location))
            .order_by("distance_to_pickup", "id")
        )

    def _get_float_query_param(self, query_params, name):
        value = query_params.get(name)
        if value in {None, ""}:
            msg = f"{name} is required when sorting by distance_to_pickup."
            raise ValidationError({name: msg})

        try:
            return float(value)
        except ValueError as exc:
            raise ValidationError({name: f"{name} must be a valid number."}) from exc
