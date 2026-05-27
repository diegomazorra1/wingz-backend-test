from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RidesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wingz_backend.rides"
    verbose_name = _("Rides")
