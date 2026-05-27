from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.test import APIRequestFactory

from wingz_backend.rides.api.views import RideViewSet

if TYPE_CHECKING:
    from wingz_backend.rides.models import Ride
    from wingz_backend.users.models import User


def test_get_queryset(ride: Ride, admin_user: User):
    view = RideViewSet()
    request = APIRequestFactory().get("/fake-url/")
    request.user = admin_user
    view.request = request

    assert ride in view.get_queryset()
