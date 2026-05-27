from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from django.urls import reverse
from rest_framework.test import APIRequestFactory

from wingz_backend.rides.api.views import RideViewSet
from wingz_backend.rides.models import Ride
from wingz_backend.rides.tests.factories import RideFactory
from wingz_backend.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from wingz_backend.users.models import User


def test_get_queryset(ride: Ride, admin_user: User):
    view = RideViewSet()
    request = APIRequestFactory().get("/fake-url/")
    request.user = admin_user
    view.request = request

    assert ride in view.get_queryset()


def test_get_queryset_filters_by_status(admin_user: User):
    requested_ride = RideFactory.create(status=Ride.Status.REQUESTED)
    completed_ride = RideFactory.create(status=Ride.Status.COMPLETED)
    view = RideViewSet()
    request = APIRequestFactory().get("/fake-url/", {"status": Ride.Status.REQUESTED})
    request.user = admin_user
    view.request = request

    queryset = view.get_queryset()

    assert requested_ride in queryset
    assert completed_ride not in queryset


def test_get_queryset_filters_by_rider_email(admin_user: User):
    rider = UserFactory.create(email="rider@example.com")
    other_rider = UserFactory.create(email="other-rider@example.com")
    matching_ride = RideFactory.create(passenger=rider)
    other_ride = RideFactory.create(passenger=other_rider)
    view = RideViewSet()
    request = APIRequestFactory().get(
        "/fake-url/",
        {"rider_email": "RIDER@example.com"},
    )
    request.user = admin_user
    view.request = request

    queryset = view.get_queryset()

    assert matching_ride in queryset
    assert other_ride not in queryset


def test_ride_list_is_paginated(admin_client):
    rides = RideFactory.create_batch(2)
    url = reverse("api:ride-list")

    response = admin_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert set(response.data) == {"count", "next", "previous", "results"}
    assert response.data["count"] == len(rides)
    assert len(response.data["results"]) == len(rides)
