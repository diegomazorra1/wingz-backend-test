from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework.viewsets import ModelViewSet

from wingz_backend.rides.api.serializers import RideSerializer
from wingz_backend.rides.models import Ride


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
        ],
    ),
)
class RideViewSet(ModelViewSet):
    serializer_class = RideSerializer
    queryset = Ride.objects.select_related("passenger", "driver")
    lookup_field = "pk"

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = getattr(self.request, "query_params", self.request.GET)
        status = query_params.get("status")
        rider_email = query_params.get("rider_email")

        if status:
            queryset = queryset.filter(status=status)

        if rider_email:
            queryset = queryset.filter(passenger__email__iexact=rider_email)

        return queryset
