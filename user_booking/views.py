from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from user_booking.models import Phone, Hotel, Personal_data, Booking
from user_booking.form import CSVUploadForm
import csv
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    hotels = Hotel.objects.all()
    return render(request, 'index.html', {'hotels': hotels})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.success(request, ("Invalid username or password, try again"))
            return redirect('user_login')
    else:
        return render(request, 'login.html')

def sign_up(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        email = request.POST['email']
        user = User.objects.create_user(username=username, email=email, password=password)
        if user is not None:
            phone_number = request.POST['phone']
            age = request.POST['age']
            shipping_address = request.POST['shipping_address']
            billing_address = request.POST['billing_address']
            business_registration_number = request.POST['business_registration_number']
            id_document = request.POST['id_document']
            id_document_number = request.POST['id_document_number']
            personal_data = Personal_data.objects.create(
                    username = username,
                    age = age,
                    email =email,
                    shipping_address = shipping_address,
                    billing_address = billing_address,
                    phone_number = phone_number,
                    business_registration_number = business_registration_number,
                    id_document = id_document,
                    id_document_number = id_document_number
            )
            personal_data.save()
            login(request, user)
            return redirect('index')
    else:
        return redirect('user_login')

@login_required
def personal_info(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        phone = request.POST['phone']
        email = request.POST['email']
        user = User.objects.create_user(username=username, email=email, password=password)
        if user is not None:
            phone = Phone(username=username, phone_number=phone)
            phone.save()
            login(request, user)
            return redirect('index')
    else:
        return render(request, 'personal_info.html')

@login_required
def upload_hotel_csv(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'This is not a CSV file.')
            else:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                next(reader)  # Skip the header row
                for row in reader:
                    try:
                        Hotel.objects.create(
                            hotel_id=row[0],
                            room_id=row[1],
                            room_type=row[2],
                            hotel_name=row[3],
                            rate=row[4],
                            supplier_contract_name=row[5],
                            contact_phone_number=row[6],
                            business_registration_number=row[7],
                            hotel_url=row[8],
                            price=row[9],
                            meal_plan=row[10]
                        )
                    except IndexError:
                        messages.error(request, f"Error in row: {row}. Please check your CSV formatting.")
                    except Exception as e:
                        messages.error(request, f"An error occurred: {str(e)}")
                        
                messages.success(request, 'Data uploaded successfully!')
    else:
        form = CSVUploadForm()

    return render(request, 'import.html', {'form': form})

@login_required
def book_hotel(request):
    if request.method == "GET":
        hotel_id = request.GET.get('hotel_id')
        rooms = Hotel.objects.filter(hotel_id=hotel_id)
        hotel = rooms[0]
        user = request.user  # Get the logged-in user
        username = user.username
        personal_info = Personal_data.objects.get(username=username)
        if personal_info is None:
            return render(request, 'book_hotel.html', {'hotel': hotel,'rooms': rooms,'user': user,})
        return render(request, 'book_hotel.html', {
            'hotel': hotel,
            'rooms': rooms,
            'user': user,
            'personal_info': personal_info
        })
    
def create_booking(request):
    if request.method == 'POST':
        username = request.user.username
        email = request.POST['email']
        age = request.POST['age']
        shipping_address = request.POST['shipping-address']
        billing_address = request.POST['billing-address']
        BRD = request.POST['BRD']
        id_document = request.POST['id-document']
        hotel_id = request.POST['hotel_id']
        room_id = request.POST['room_id']
        check_in_date = request.POST['check_in_date']
        check_out_date = request.POST['check_out_date']
        booking_status = request.POST['booking_status']

        personal_info = Personal_data.objects.get(username=username)
        personal_info.email = email
        personal_info.shipping_address = shipping_address
        personal_info.billing_address = billing_address
        personal_info.business_registration_number = BRD
        personal_info.age = age
        personal_info.id_document = id_document
        personal_info.save()

        booking_record = Booking.objects.create(username=username, hotel_id=hotel_id, room_id=room_id, booking_status=booking_status, check_in_date=check_in_date, check_out_date=check_out_date)
        booking_record.save()
        return redirect('index')
# display specific bookings    
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'booking_detail.html', {'booking': booking})
