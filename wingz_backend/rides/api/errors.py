from rest_framework.exceptions import APIException


class InvalidRideStatusTransition(APIException):
    status_code = 409
    default_code = "invalid_ride_status_transition"

    def __init__(self, current_status: str, requested_status: str) -> None:
        super().__init__(
            f"Cannot change ride status from {current_status} to {requested_status}.",
        )
