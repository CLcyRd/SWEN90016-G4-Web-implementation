from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),  
    path('user_login/', views.user_login, name='user_login'),  
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('personal_info/', views.personal_info, name='personal_info'),
    path('upload/', views.upload_hotel_csv, name='upload_hotel_csv'),
    path('book_hotel/', views.book_hotel, name='book_hotel'),
    path('create_booking/', views.create_booking, name='create_booking'),
    path('admin/booking/<int:pk>/', views.booking_detail, name='booking_detail'),
]

