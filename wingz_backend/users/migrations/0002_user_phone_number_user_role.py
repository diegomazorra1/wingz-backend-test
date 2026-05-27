from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="phone_number",
            field=models.CharField(blank=True, max_length=32, verbose_name="phone number"),
        ),
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("passenger", "Passenger"), ("driver", "Driver")],
                default="passenger",
                max_length=20,
                verbose_name="role",
            ),
        ),
    ]
