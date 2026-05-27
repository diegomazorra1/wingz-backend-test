from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import gettext_lazy as _


class Ride(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", _("Requested")
        EN_ROUTE = "en_route", _("En route")
        PICKUP = "pickup", _("Pickup")
        DROPOFF = "dropoff", _("Dropoff")
        COMPLETED = "completed", _("Completed")
        CANCELED = "canceled", _("Canceled")

    passenger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requested_rides",
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="assigned_rides",
    )
    pickup_address = models.CharField(blank=True, max_length=255)
    dropoff_address = models.CharField(blank=True, max_length=255)
    pickup_latitude = models.DecimalField(
        blank=True,
        decimal_places=6,
        max_digits=9,
        null=True,
    )
    pickup_longitude = models.DecimalField(
        blank=True,
        decimal_places=6,
        max_digits=9,
        null=True,
    )
    pickup_location = gis_models.PointField(
        blank=True,
        geography=True,
        null=True,
        spatial_index=True,
    )
    dropoff_latitude = models.DecimalField(
        blank=True,
        decimal_places=6,
        max_digits=9,
        null=True,
    )
    dropoff_longitude = models.DecimalField(
        blank=True,
        decimal_places=6,
        max_digits=9,
        null=True,
    )
    scheduled_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        choices=Status.choices,
        db_index=True,
        default=Status.REQUESTED,
        max_length=20,
    )
    fare_amount = models.DecimalField(
        blank=True,
        decimal_places=2,
        max_digits=10,
        null=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["scheduled_at"], name="ride_pickup_time_idx"),
        ]

    def __str__(self) -> str:
        return f"Ride #{self.pk} - {self.status}"
