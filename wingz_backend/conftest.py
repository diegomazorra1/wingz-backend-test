from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from wingz_backend.rides.tests.factories import RideFactory
from wingz_backend.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from wingz_backend.rides.models import Ride
    from wingz_backend.users.models import User


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory.create()


@pytest.fixture
def ride(db, user: User) -> Ride:
    return RideFactory.create(passenger=user)
