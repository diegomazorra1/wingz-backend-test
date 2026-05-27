from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import resolve
from django.urls import reverse

if TYPE_CHECKING:
    from wingz_backend.rides.models import Ride


def test_ride_detail(ride: Ride):
    assert (
        reverse("api:ride-detail", kwargs={"pk": ride.pk}) == f"/api/rides/{ride.pk}/"
    )
    assert resolve(f"/api/rides/{ride.pk}/").view_name == "api:ride-detail"


def test_ride_list():
    assert reverse("api:ride-list") == "/api/rides/"
    assert resolve("/api/rides/").view_name == "api:ride-list"
