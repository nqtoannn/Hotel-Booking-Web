from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_home),
    path('test/<int:pagenumber>', views.hotelList),
    path('home', views.testui, name='home'),
    path('register/', views.register, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('booking_detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('booking_list/', views.booking_list, name='booking_list'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('search', views.search, name="search"),
    path('hotel/<int:hotelcode>', views.hotel_detail, name='hotel_detail'),
    path('rate_hotel/', views.rate_hotel, name='rate_hotel'),
    path('rating_list/', views.rating_list, name='rating_list'),
    path('add_wishlist/<int:roomid>', views.add_wishlist, name='add_wishlist'),
    path('hotel_list/<int:pagenumber>', views.hotel_list, name='hotel_list'),
    path('new_booking/<int:roomid>/<str:dayin>/<str:dayout>', views.new_booking, name='new_booking'),
]   
