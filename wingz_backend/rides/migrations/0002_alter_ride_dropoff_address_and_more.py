from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("rides", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ride",
            name="dropoff_address",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="ride",
            name="pickup_address",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
