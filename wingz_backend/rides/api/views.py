from rest_framework.viewsets import ModelViewSet

from wingz_backend.rides.api.serializers import RideSerializer
from wingz_backend.rides.models import Ride


class RideViewSet(ModelViewSet):
    serializer_class = RideSerializer
    queryset = Ride.objects.select_related("passenger", "driver")
    lookup_field = "pk"
