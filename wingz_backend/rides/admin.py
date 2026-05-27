from django.contrib import admin

from wingz_backend.rides.models import Ride
from wingz_backend.rides.models import RideEvent


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "passenger",
        "driver",
        "pickup_address",
        "dropoff_address",
        "status",
        "scheduled_at",
        "created_at",
    ]
    list_filter = ["status", "scheduled_at", "created_at"]
    search_fields = [
        "passenger__email",
        "driver__email",
        "pickup_address",
        "dropoff_address",
    ]
    autocomplete_fields = ["passenger", "driver"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "ride",
        "description",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = [
        "ride__passenger__email",
        "ride__driver__email",
        "description",
    ]
    autocomplete_fields = ["ride"]
    readonly_fields = ["created_at"]
