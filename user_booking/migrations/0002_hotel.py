# Generated by Django 4.2.16 on 2024-09-18 09:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_booking", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Hotel",
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
                ("hotel_id", models.IntegerField(max_length=1000000)),
                ("room_id", models.IntegerField(max_length=1000000)),
                ("room_type", models.CharField(max_length=40)),
                ("hotel_name", models.CharField(max_length=100)),
                ("rate", models.IntegerField(max_length=100)),
                ("supplier_contract_name", models.CharField(max_length=100)),
                ("contact_phone_number", models.IntegerField(max_length=100)),
                (
                    "business_registration_number",
                    models.IntegerField(max_length=100000),
                ),
                ("hotel_url", models.URLField()),
                ("price", models.IntegerField(max_length=100000)),
                ("meal_plan", models.CharField(max_length=100000)),
            ],
        ),
    ]
