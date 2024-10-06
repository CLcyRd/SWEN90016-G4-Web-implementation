from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from user_booking.models import Phone, Hotel, Personal_data, Booking, Hotel_data, Room_data
from user_booking.form import CSVUploadForm
import csv
import pandas
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError

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

        # 检查用户名是否已经存在
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different username.")
            return redirect('sign_up')  # 重定向到注册页面，让用户重新输入

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

            # 保存用户详细信息到 Personal_data 表
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

            # 发送欢迎邮件
            send_mail(
                'Welcome to Our Service!',
                f'Hello {username}, welcome to our platform. We are happy to have you on board!',
                'admin@hotelbooking.com',  # 发件人
                [email],  # 收件人是用户注册时输入的邮箱
                fail_silently=False,
            )

            login(request, user)  # 登录用户
            return redirect('index')
    else:
        return render(request, 'login.html')  # 如果是 GET 请求，返回登录页面

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
