# Generated by Django 4.2.16 on 2024-09-18 11:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_booking", "0004_hotel_address"),
    ]

    operations = [
        migrations.CreateModel(
            name="Booking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("username", models.CharField(max_length=20)),
                ("hotel_id", models.IntegerField()),
                ("room_id", models.IntegerField()),
                ("booking_status", models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name="Personal_data",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("username", models.CharField(max_length=20)),
                ("age", models.IntegerField(default=18)),
                ("address", models.CharField(max_length=100)),
                ("phone_number", models.CharField(max_length=20)),
                ("business_registration_number", models.CharField(max_length=100)),
                ("id_document", models.CharField(max_length=40)),
                ("id_document_number", models.CharField(max_length=40)),
            ],
        ),
    ]
