from django.contrib import admin
from .models import Phone, Hotel, Personal_data, Booking, Hotel_data, Room_data
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.urls import path  # Import the path function

admin.site.register(Hotel)
admin.site.register(Hotel_data)
admin.site.register(Room_data)
admin.site.register(Personal_data)
# admin.site.register(Booking)


# These are the admin actions for bookings

# status of selected bookings from "ONHOLD" to "RELEASED" if they are in the "ONHOLD" status
def release_bookings(modeladmin, request, queryset):
    # Filter to only apply to bookings with ONHOLD status
    queryset = queryset.filter(booking_status='ONHOLD')
    if queryset.exists():
        updated = queryset.update(booking_status='RELEASED')
        modeladmin.message_user(request, f"{updated} bookings were successfully released.")
    else:
        modeladmin.message_user(request, "No ONHOLD bookings selected.", level=messages.WARNING)
# status of selected bookings from "ONHOLD" to "CONFIRMED" if they are in the "ONHOLD" status
def confirm_bookings(modeladmin, request, queryset):
    # Filter to only apply to bookings with ONHOLD status
    queryset = queryset.filter(booking_status='ONHOLD')
    if queryset.exists():
        updated = queryset.update(booking_status='CONFIRMED')
        modeladmin.message_user(request, f"{updated} bookings were successfully confirmed.")
    else:
        modeladmin.message_user(request, "No ONHOLD bookings selected.", level=messages.WARNING)

# status of selected bookings from "CONFIRMED" to "CANCELLED" if they are in the "CONFIRMED" status
def cancel_bookings(modeladmin, request, queryset):
    # Filter to only apply to bookings with CONFIRMED status
    queryset = queryset.filter(booking_status='CONFIRMED')
    if queryset.exists():
        updated = queryset.update(booking_status='CANCELLED')
        modeladmin.message_user(request, f"{updated} bookings were successfully cancelled.")
    else:
        modeladmin.message_user(request, "No CONFIRMED bookings selected.", level=messages.WARNING)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    #  fields are shown
    list_display = ('booking_id', 'username', 'hotel_id', 'room_id', 'check_in_date', 'check_out_date', 'booking_status', 'creation_date', 'view_booking')
    # filter sidebar
    list_filter = ('booking_status',)
    # fields for search functionality
    search_fields = ('booking_id', 'username')
    # order fields
    ordering = ('-creation_date',)
    actions = [release_bookings, confirm_bookings, cancel_bookings]

    # Create link to custom booking view
    def view_booking(self, obj):
            return format_html('<a href="{}">View Booking</a>', reverse('admin:booking_detail', args=[obj.pk]))

    view_booking.short_description = 'View Booking'
    view_booking.allow_tags = True
# This is supposed to show or hide actions based on the selected bookings status -- not polished!
    def get_actions(self, request):
        actions = super().get_actions(request)
        selected_bookings = request.POST.getlist('_selected_action')

        if selected_bookings:
            queryset = self.model.objects.filter(pk__in=selected_bookings)

            # if no ONHOLD bookings
            if not queryset.filter(booking_status='ONHOLD').exists():
                actions.pop('release_bookings', None)
                actions.pop('confirm_bookings', None)

            # if no CONFIRMED bookings
            if not queryset.filter(booking_status='CONFIRMED').exists():
                actions.pop('cancel_bookings', None)

        return actions
    # this is gonna be a custom URL pattern for the booking detail view
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:pk>/', self.admin_site.admin_view(self.booking_detail), name='booking_detail'),
        ]
        return custom_urls + urls
    # renders booking view
    def booking_detail(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        context = dict(
            self.admin_site.each_context(request),
            booking=booking,
        )
        return render(request, 'admin/booking_detail.html', context)

    
