from django.contrib import admin
from .models import Phone, Hotel, Personal_data, Booking

admin.site.register(Phone)
admin.site.register(Hotel)
admin.site.register(Personal_data)
admin.site.register(Booking)