from __future__ import annotations

from wingz_backend.users.models import User


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/users/{user.pk}/"


def test_user_defaults_to_passenger_role(user: User):
    assert user.role == User.Role.PASSENGER
