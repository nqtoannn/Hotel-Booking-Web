from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.forms import UserCreationForm
from django import forms
# Create your models here.

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields=['username','email','first_name','last_name','password1','password2']
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=False)
    name = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=200, null=True)
    password = models.CharField(max_length=100, null=True)
    def __str__(self):
        return self.name

class UserPreferences(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True)
    city = models.CharField(max_length=200, null=True)
    number = models.CharField(max_length=50, null=True)
    feature = models.CharField(max_length=100, null=True)
    createAt = models.DateTimeField(auto_now_add=True)
    weight = models.CharField(max_length=50, null=True)
    def __str__(self):
        return self.feature

class BookingHotel(models.Model):
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True)
    roomId = models.CharField(max_length=200, null=True)
    date_booking = models.DateTimeField(auto_now_add=True)
    date_in = models.DateTimeField(null=True)
    date_return = models.DateTimeField(null=True)
    status = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.user.name} booked {self.roomId}'
        
class WishList(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True) 
    roomId = models.CharField(max_length=200, null=True)
    saved_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.roomId} is favorite of {self.user.name}'
    
class Rating(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    roomId = models.CharField(max_length=200, null=True)
    value = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.user.name} rated {self.roomId} with {self.value} stars'