from wingz_backend.rides.api.errors import InvalidRideStatusTransition
from wingz_backend.rides.models import Ride
from wingz_backend.rides.models import RideEvent

TERMINAL_STATUSES = {Ride.Status.CANCELED, Ride.Status.COMPLETED}


def validate_ride_status_transition(current_status: str, requested_status: str) -> None:
    if (
        requested_status
        and requested_status != current_status
        and current_status in TERMINAL_STATUSES
    ):
        raise InvalidRideStatusTransition(current_status, requested_status)


def record_ride_created(ride: Ride) -> None:
    RideEvent.objects.create(ride=ride, description="Ride created")


def record_ride_status_changed(ride: Ride) -> None:
    RideEvent.objects.create(
        ride=ride,
        description=f"Status changed to {ride.status}",
    )
