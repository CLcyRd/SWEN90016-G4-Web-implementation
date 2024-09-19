# Generated by Django 4.2.16 on 2024-09-19 05:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_booking", "0007_booking_check_in_date_booking_check_out_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="booking",
            name="id",
        ),
        migrations.AddField(
            model_name="booking",
            name="booking_id",
            field=models.UUIDField(
                default=1, editable=False, primary_key=True, serialize=False
            ),
            preserve_default=False,
        ),
    ]
