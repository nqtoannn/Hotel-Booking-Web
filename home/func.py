from datetime import datetime
from .models import *

def bookHotel(user, roomId, create_at, day_in, day_out):
    booking = BookingHotel(user=user, roomId=roomId, date_booking=create_at, date_in = day_in, date_return = day_out)
    booking.save()

def rateHotel(user, roomId, value):
    rating = Rating.objects.create(
            user=user,
            roomId=roomId,
            value=value
        )

def addWishList(user, roomId):
    WishList.objects.get_or_create(user=user, roomId=roomId)
    
def create_user_preference(user_profile, city, number, feature, weight):
    user_preference = UserPreferences.objects.create(
        user=user_profile,
        city=city,
        number=number,
        feature=feature,
        weight = weight 
    )
    return user_preference