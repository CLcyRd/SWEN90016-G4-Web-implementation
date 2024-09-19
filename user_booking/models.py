from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class Phone(models.Model):
    username = models.CharField(max_length=20)
    phone_number = models.IntegerField(max_length=20)
    
    def __str__(self):
        return f"{self.username} - {self.phone_number}"
    

class Hotel(models.Model):
    hotel_id = models.IntegerField()
    room_id = models.IntegerField()
    room_type = models.CharField(max_length=40)
    hotel_name = models.CharField(max_length=100)
    rate = models.IntegerField()
    supplier_contract_name = models.CharField(max_length=100)
    contact_phone_number = models.CharField(max_length=15)
    business_registration_number = models.CharField(max_length=100)
    hotel_url = models.URLField()
    price = models.IntegerField()
    meal_plan = models.CharField(max_length=100)
    address = models.CharField(max_length=255, default="melbourne")  # Add an address field

    def __str__(self):
        return f"{self.hotel_name} - {self.room_type}"
    
class Personal_data(models.Model):
    username = models.CharField(max_length=20)
    age = models.IntegerField(default=18)
    email = models.CharField(max_length=30, default=' ')
    shipping_address = models.CharField(max_length=100, default=' ')
    billing_address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    business_registration_number = models.CharField(max_length=100)
    id_document = models.CharField(max_length=40)
    id_document_number = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.username}"
    
class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True, editable=False)
    username = models.CharField(max_length=20)
    hotel_id = models.IntegerField()
    room_id = models.IntegerField()
    check_in_date = models.DateField(default=datetime.date.today)
    check_out_date = models.DateField(default=datetime.date.today)
    booking_status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.username} - {self.hotel_id}"