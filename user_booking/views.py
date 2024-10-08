from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from user_booking.models import Phone, Hotel, Personal_data, Booking, Hotel_data, Room_data
from user_booking.form import CSVUploadForm
import csv
import pandas
import requests
import hotel_booking.settings as settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
import django.template.loader
from datetime import datetime, timedelta


# Create your views here.
def index(request):
    # Fetch all hotel data
    hotels = Hotel_data.objects.all()
    hotel_room_data = []

    for hotel in hotels:
        # Fetch the corresponding room data for each hotel
        rooms = Room_data.objects.filter(hotel_id=hotel.hotel_id)

        # Combine hotel and room data
        for room in rooms:
            hotel_room_data.append({
                'hotel_id': hotel.hotel_id,
                'hotel_name': hotel.hotel_name,
                'room_type': room.room_type,
                'rate': hotel.rate,
                'supplier_contract_name': hotel.supplier_contract_name,
                'contact_phone_number': hotel.contact_phone_number,
                'business_registration_number': hotel.business_registration_number,
                'hotel_url': hotel.hotel_url,
                'price': room.price,
                'meal_plan': hotel.meal_plan,
                'address': hotel.address,
                'room_image': room.room_image,
            })

    return render(request, 'index.html', {'hotels': hotel_room_data})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        locked = request.session.get('lock_time')
        failed_attempts = request.session.get('failed_attempts', 0)

    
        # Check if the user is currently locked out
        if locked:
            locked = datetime.fromtimestamp(locked)
            if datetime.now() < locked:
                minutes_left = (locked- datetime.now()).seconds // 60
                messages.error(request, f"You have been locked out. Try again in {minutes_left} minute(s).")
                return render(request, 'login.html')
        if failed_attempts >= 5:
                lock_time = datetime.now() + timedelta(minutes=10)
                request.session['lock_time'] = lock_time.timestamp()
                messages.error(request, "Too many failed attempts. Please try again after 10 minutes.")
                failed_attempts = 0
                return render(request, 'login.html')
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.success(request, ("Invalid username or password, try again"))
            failed_attempts += 1  # Increment failed attempts
            request.session['failed_attempts'] = failed_attempts
            return redirect('user_login')
    else:
        return render(request, 'login.html')
    

def sign_up(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        otp = request.POST['verify']
        recaptcha_response = request.POST.get('g-recaptcha-response')
        locked = request.session.get('lock_time')
        failed_attempts = request.session.get('failed_attempts', 0)

    
        # Check if the user is currently locked out
        if locked:
            locked = datetime.fromtimestamp(locked)
            if datetime.now() < locked:
                minutes_left = (locked- datetime.now()).seconds // 60
                messages.error(request, f"You have been locked out. Try again in {minutes_left} minute(s).")
                return render(request, 'login.html')
            
        if failed_attempts >= 5:
                lock_time = datetime.now() + timedelta(minutes=10)
                request.session['lock_time'] = lock_time.timestamp()
                messages.error(request, "Too many failed attempts. Please try again after 10 minutes.")
                failed_attempts = 0
                return render(request, 'login.html')
        
        stored_otp = request.session.get('verify') 
        otp_timestamp = request.session.get('otp_timestamp')
        # Verify reCAPTCHA
        recaptcha_validation = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': settings.RECAPTCHA_PRIVATE_KEY,  # Ensure RECAPTCHA_SECRET_KEY is in settings.py
                'response': recaptcha_response
            }
        )

        result = recaptcha_validation.json()
        if not result.get('success'):
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            failed_attempts += 1  # Increment failed attempts
            request.session['failed_attempts'] = failed_attempts
            return render(request, 'login.html')
        
        # Check if already stored
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different username.")
            failed_attempts += 1  # Increment failed attempts
            request.session['failed_attempts'] = failed_attempts
            return render(request, 'login.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists. Please use a different email.")
            failed_attempts += 1  # Increment failed attempts
            request.session['failed_attempts'] = failed_attempts
            return render(request, 'login.html')
        # check whether the verification code is correct
        
        if stored_otp == None:
            print('error1')
            messages.error(request, "No verification code found. Please request a new one.")
            failed_attempts += 1  # Increment failed attempts
            request.session['failed_attempts'] = failed_attempts
            return render(request, 'login.html')

        if otp != stored_otp:  # If OTP does not match
            print('error2')
            messages.error(request, "Verification code does not match. Please try again.")
            failed_attempts += 1  # Increment failed attempts
            request.session['failed_attempts'] = failed_attempts
            return render(request, 'login.html')  # Redirect back to the sign-up page
        
        if stored_otp is None or otp_timestamp is None:
            messages.error(request, "No verification code found. Please request a new one.")
            failed_attempts += 1  # Increment failed attempts
            request.session['failed_attempts'] = failed_attempts
            return render(request, 'login.html')
        
        otp_time = datetime.fromtimestamp(otp_timestamp)
        if datetime.now() > otp_time + timedelta(minutes=10):
            messages.error(request, "The verification code has expired. Please request a new one.")
            failed_attempts += 1  # Increment failed attempts
            request.session['failed_attempts'] = failed_attempts
            return render(request, 'login.html')
        
        # 创建用户
        user = User.objects.create_user(username=username, email=email, password=password)
        
        if user is not None:
            phone_number = request.POST['phone']
            age = request.POST['age']
            shipping_address = request.POST['shipping_address']
            billing_address = request.POST['billing_address']
            business_registration_number = request.POST['business_registration_number']
            id_document = request.POST['id_document']
            id_document_number = request.POST['id_document_number']

            # Store
            personal_data = Personal_data.objects.create(
                username=username,
                age=age,
                email=email,
                shipping_address=shipping_address,
                billing_address=billing_address,
                phone_number=phone_number,
                business_registration_number=business_registration_number,
                id_document=id_document,
                id_document_number=id_document_number
            )
            personal_data.save()
            html_message = django.template.loader.render_to_string('welcome.html', {'username': username})
            # Send email
            send_mail(
                'Welcome to Our Service!',
                '',
                'admin@hotelbooking.com',  # admin emaiil
                [email],
                html_message=html_message,  # user email
                fail_silently=False,
            )
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)  # login
            return redirect('index')
    else:
        return render(request, 'login.html')  # back to login

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
            user.backend = 'django.contrib.auth.backends.ModelBackend'
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
                try:
                    df = pandas.read_csv(csv_file)
                    errors = []
                    
                    for index, row in df.iterrows():
                        # Check if the hotel with the same name already exists
                        if Hotel_data.objects.filter(hotel_name=row['hotel_name']).exists():
                            errors.append(f"Hotel '{row['hotel_name']}' already exists.")
                        else:
                            # Create the hotel data
                            hotel = Hotel_data.objects.create(
                                hotel_name=row['hotel_name'],
                                rate=row['rate'],
                                supplier_contract_name=row['supplier_contract_name'],
                                contact_phone_number=row['contact_phone_number'],
                                business_registration_number=row['business_registration_number'],
                                hotel_url=row['hotel_url'],
                                meal_plan=row['meal_plan'],
                                address=row['address']
                            )

                            # Create the room data
                            try:
                                Room_data.objects.create(
                                    hotel_id=hotel.hotel_id,
                                    room_type=row['room_type'],
                                    price=row['price'],
                                    inventory=0  # Assuming inventory is 0 in this example
                                )
                            except IntegrityError:
                                errors.append(f"Room '{row['room_type']}' for Hotel '{row['hotel_name']}' already exists.")


                    if errors:
                        return render(request, 'import.html', {'form': form, 'errors': errors})

                    return redirect('success')  # Redirect to a success page
                except Exception as e:
                    print(e)
                    return render(request, 'import.html', {'form': form, 'error': str(e)})
    else:
        form = CSVUploadForm()

    return render(request, 'import.html', {'form': form})

@login_required
def book_hotel(request):
    if request.method == "GET":
        hotel_id = request.GET.get('hotel_id')
        
        # Get the hotel details from Hotel_data model
        hotel = get_object_or_404(Hotel_data, hotel_id=hotel_id)
        
        # Get the available rooms for the hotel from Room_data model
        rooms = Room_data.objects.filter(hotel_id=hotel_id)
        
        # Get the current logged-in user
        user = request.user  
        username = user.username
        
        # Get the personal information of the logged-in user
        personal_info = Personal_data.objects.filter(username=username).first()
        
        # Pass the hotel, rooms, and user data to the template
        return render(request, 'book_hotel.html', {
            'hotel': hotel,
            'rooms': rooms,
            'user': user,
            'personal_info': personal_info
        })
    
from django.core.mail import send_mail

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

        booking_record = Booking.objects.create(
            username=username, 
            hotel_id=hotel_id, 
            room_id=room_id, 
            booking_status=booking_status, 
            check_in_date=check_in_date, 
            check_out_date=check_out_date
        )
        booking_record.save()

        # 发送确认邮件
        send_mail(
            'Booking Confirmation',
            f'Hi {username}, your booking for hotel {hotel_id} has been confirmed from {check_in_date} to {check_out_date}.',
            'admin@hotelbooking.com',  # 发件人
            [email],  # 收件人
            fail_silently=False,
        )

        

        return redirect('index')
    
# display specific bookings    
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'booking_detail.html', {'booking': booking})


def existUser(sendingEmail):
    return (Personal_data.objects.filter(email=sendingEmail).exists() or User.objects.filter(email=sendingEmail).exists()) #Checks users OR superusers consider it fixed

def reg(request):

    response = {"state": False, "errmsg": "11111"} # set default response
    email = request.POST.get('email')

    if request.POST.get('type') == 'sendOTP':

        csrf_token = request.POST.get('csrfmiddlewaretoken')
        print("Received CSRF token:", csrf_token)

        email = request.POST.get('email')

        response = {"state": False, "errmsg": ""} # set default response

        if existUser(email):
            
            response['state'] = False
            response['errmsg'] = 'Email Exists! Log in please!'
            print("Email Exists! Log in please!")

        else:
            try:
                print(str(existUser(email)))
                rand_str = sendMessage(request,email)  # Send email
                request.session['verify'] = rand_str  # Store code into session
                print(request.session['verify'])
                response['state'] = True
                print("Message Sent!")
            except:
                response['state'] = False
                response['errmsg'] = 'Unable to send code, please check email'
                print("Unable to send code, please check email")
        
        print("11111Email:", email)
        return JsonResponse(response)
    
    print("22222Email:", email)
    return JsonResponse(response)
    

def sendMessage(request,email):

    # Generate verification code
    import random
    str1 = '0123456789'
    rand_str = ''.join(random.choice(str1) for _ in range(6))

    # Render the HTML email template
    html_message = django.template.loader.render_to_string('email_template.html', {'code': rand_str})

    # Send email
    emailBox = [email]
    send_mail(
        'Your Verification Code',
        '',  # Empty since we're using the HTML template
        'your-email@example.com',
        emailBox,
        fail_silently=False,
        html_message=html_message  # Sending the rendered HTML message
    )
    request.session['verify'] = rand_str
    request.session['otp_timestamp'] = datetime.now().timestamp()
    return rand_str
