# Generated by Django 4.2.16 on 2024-10-02 10:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_booking", "0013_room_data_inventory"),
    ]

    operations = [
        migrations.AddField(
            model_name="room_data",
            name="room_image",
            field=models.ImageField(blank=True, null=True, upload_to=""),
        ),
    ]
