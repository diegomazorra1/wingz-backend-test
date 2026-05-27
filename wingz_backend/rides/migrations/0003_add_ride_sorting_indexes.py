import django.contrib.gis.db.models.fields
import django.contrib.postgres.operations
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("rides", "0002_alter_ride_dropoff_address_and_more"),
    ]

    operations = [
        django.contrib.postgres.operations.CreateExtension("postgis"),
        migrations.AddField(
            model_name="ride",
            name="pickup_location",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True,
                geography=True,
                null=True,
                spatial_index=True,
                srid=4326,
            ),
        ),
        migrations.AddIndex(
            model_name="ride",
            index=models.Index(fields=["scheduled_at"], name="ride_pickup_time_idx"),
        ),
    ]
