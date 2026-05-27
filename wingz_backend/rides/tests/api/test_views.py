from __future__ import annotations

from datetime import timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from wingz_backend.rides.api.views import RideViewSet
from wingz_backend.rides.models import Ride
from wingz_backend.rides.tests.factories import RideEventFactory
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


def test_get_queryset_sorts_by_pickup_time(admin_user: User):
    later_ride = RideFactory.create(scheduled_at=timezone.now() + timedelta(hours=1))
    earlier_ride = RideFactory.create(scheduled_at=timezone.now())
    view = RideViewSet()
    request = APIRequestFactory().get("/fake-url/", {"sort": "pickup_time"})
    request.user = admin_user
    view.request = request

    queryset = view.get_queryset()

    assert list(queryset[:2]) == [earlier_ride, later_ride]


def test_get_queryset_sorts_by_distance_to_pickup(admin_user: User):
    near_ride = RideFactory.create(
        pickup_latitude="37.775000",
        pickup_longitude="-122.419500",
    )
    far_ride = RideFactory.create(
        pickup_latitude="37.900000",
        pickup_longitude="-122.500000",
    )
    view = RideViewSet()
    request = APIRequestFactory().get(
        "/fake-url/",
        {
            "sort": "distance_to_pickup",
            "latitude": "37.774900",
            "longitude": "-122.419400",
        },
    )
    request.user = admin_user
    view.request = request

    queryset = view.get_queryset()

    assert list(queryset[:2]) == [near_ride, far_ride]


def test_get_queryset_requires_gps_position_for_distance_sort(admin_user: User):
    view = RideViewSet()
    request = APIRequestFactory().get("/fake-url/", {"sort": "distance_to_pickup"})
    request.user = admin_user
    view.request = request

    with pytest.raises(ValidationError):
        view.get_queryset()


def test_ride_list_is_paginated(admin_client):
    rides = RideFactory.create_batch(2)
    url = reverse("api:ride-list")

    response = admin_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert set(response.data) == {"count", "next", "previous", "results"}
    assert response.data["count"] == len(rides)
    assert len(response.data["results"]) == len(rides)


def test_ride_list_sorts_by_distance_to_pickup_with_pagination(admin_client):
    near_ride = RideFactory.create(
        pickup_latitude="37.775000",
        pickup_longitude="-122.419500",
    )
    RideFactory.create(
        pickup_latitude="37.900000",
        pickup_longitude="-122.500000",
    )
    url = reverse("api:ride-list")

    response = admin_client.get(
        url,
        {
            "sort": "distance_to_pickup",
            "latitude": "37.774900",
            "longitude": "-122.419400",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.data["results"][0]["id"] == near_ride.id


def test_ride_list_returns_only_recent_ride_events(admin_client):
    ride = RideFactory.create()
    recent_event = RideEventFactory.create(
        ride=ride,
        description="Ride created recently.",
    )
    old_event = RideEventFactory.create(
        ride=ride,
        description="Ride created more than 24 hours ago.",
    )
    old_event.created_at = timezone.now() - timedelta(hours=25)
    old_event.save(update_fields=["created_at"])
    url = reverse("api:ride-list")

    response = admin_client.get(url)

    assert response.status_code == HTTPStatus.OK
    [ride_data] = response.data["results"]
    assert len(ride_data["todays_ride_events"]) == 1
    [event_data] = ride_data["todays_ride_events"]
    assert event_data["id"] == recent_event.id
    assert event_data["description"] == recent_event.description


def test_ride_list_prefetches_todays_events_in_constant_queries(admin_user):
    rides = RideFactory.create_batch(2)
    for ride in rides:
        RideEventFactory.create(ride=ride)
        RideEventFactory.create(ride=ride)

    view = RideViewSet.as_view({"get": "list"})
    request = APIRequestFactory().get("/api/rides/")
    force_authenticate(request, user=admin_user)

    with CaptureQueriesContext(connection) as queries:
        response = view(request)

    expected_query_count = 3
    assert response.status_code == HTTPStatus.OK
    assert len(queries) == expected_query_count
