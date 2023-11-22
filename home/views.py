from django.shortcuts import render,redirect, get_object_or_404
from .hotel_recomemdation import requirementbased, random_forest_based, citybased
from .models import *
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .func import *
from django.core.exceptions import ObjectDoesNotExist
from .hotel_search import *
import random
# Create your views here.

def search(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    user_profile = UserProfile.objects.get(user=request.user) 
    if request.method == "POST":
        description_hotel = request.POST['descriptionHotel'] 
        city = request.POST['city'] 
        number_of = int(request.POST['numberOf'])
        print("in search: ", city, number_of, description_hotel)
        if number_of is None and description_hotel is None:
            output = citybased(city)
        else:
            output = requirementbased(city,number_of,description_hotel)
            create_user_preference(user_profile,city,number_of,description_hotel,25)
        hotelList = get_hotels_data_by_codes(output)
        print(hotelList)
        context = {'hotelList': hotelList, "city": city, "descriptionHotel": description_hotel, "numberOf": number_of}
        return render(request, 'search.html', context)
    context = {}
    return render(request,'search.html',context)

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_profile = UserProfile()
            user_profile.user = user
            user_profile.name = request.POST['first_name'] + ' ' + request.POST['last_name'] # Lấy giá trị tên từ biểu mẫu
            user_profile.email = request.POST['email']  # Lấy giá trị email từ biểu mẫu
            user_profile.password = request.POST['password1']  # Lấy giá trị mật khẩu từ biểu mẫu
            user_profile.save()
            return redirect('login')
        else: 
            message = "Account already exists, please try again!"
            return render(request, 'register.html', {'message': message} )
    context ={'form':form}
    return render(request,'register.html',context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect(get_home)
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect(get_home)
        else: 
            message = "Wrong username or password. Please try again!"
            return render(request, 'login.html', {'message': message})
    context ={}
    return render(request,'login.html',context)

def logoutPage(request):
    logout(request)
    return redirect(loginPage)

def get_home(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    username = request.user.first_name + " " + request.user.last_name
    user_profile = UserProfile.objects.get(user=request.user) 
    try:
        userPreferenceslist = UserPreferences.objects.filter(user=user_profile)
    except ObjectDoesNotExist:
        userPreferenceslist = None 
    if userPreferenceslist is not None:
        hotel_code_list =[]
        for userPreferences in userPreferenceslist:
            hotel_code_list = random_forest_based(userPreferences.city, int(userPreferences.number), userPreferences.feature) + hotel_code_list
        print(hotel_code_list)
    else:
        city = 'london'
        number = 4
        features = 'I need a room with free wifi'
        hotel_code_list = random_forest_based(city, number, features)
        print(hotel_code_list) 
    hotel_list = get_hotels_data_by_codes(hotel_code_list)
    context = {'username': username, 'result': hotel_list}
    return render(request, 'home.html', context) 


def new_booking(request, roomid, dayin, dayout):
    if not request.user.is_authenticated:
        return redirect('login') 
    roomId = roomid
    userProfile = UserProfile.objects.get(user=request.user)
    create_at = datetime.now()
    day_in = datetime.strptime(dayin, "%Y-%m-%d").date()
    day_out =  datetime.strptime(dayout, "%Y-%m-%d").date()
    bookHotel(userProfile, roomId, create_at,day_in,day_out)
    user = UserProfile.objects.get(user=request.user)
    bookings = BookingHotel.objects.filter(user=user)
    userPreferences = getUserPreferencesByRoom(roomid)
    create_user_preference(userProfile,userPreferences[0],userPreferences[1],userPreferences[2],50)
    return render(request, 'booking_list.html', {'bookings': bookings})

def booking_detail(request, booking_id):
    if not request.user.is_authenticated:
        return redirect('login') 
    booking = get_object_or_404(BookingHotel, booking_id=booking_id)
    return render(request, 'booking_detail.html', {'booking': booking})

def booking_list(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    user = UserProfile.objects.get(user=request.user)
    bookings = BookingHotel.objects.filter(user=user)
    return render(request, 'booking_list.html', {'bookings': bookings})

def add_wishlist(request, roomid):
    if not request.user.is_authenticated:
        return redirect('login') 
    user = UserProfile.objects.get(user=request.user)
    WishList.objects.get_or_create(user=user, roomId=roomid)
    hotelcode = get_hotelcode_by_room(roomid)
    userProfile = UserProfile.objects.get(user=request.user)
    userPreferences = getUserPreferencesByRoom(roomid)
    create_user_preference(userProfile,userPreferences[0],userPreferences[1],userPreferences[2],75)
    return redirect('hotel_detail', hotelcode=hotelcode)


def wishlist(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    user = UserProfile.objects.get(user=request.user) 
    wishlist_items = WishList.objects.filter(user=user)
    return render(request, "wishlist.html", {'wishlist_items': wishlist_items})


def hotel_detail(request,hotelcode):
    if not request.user.is_authenticated:
        return redirect('login') 
    listroom = get_room_in_hotel(hotelcode)
    user = UserProfile.objects.get(user=request.user)
    wishlist_items = set(WishList.objects.filter(user=user).values_list('roomId', flat=True).distinct())
    output = []
    hotel_room_image_path = os.path.join(current_directory, 'data-set', 'image_room.csv')
    
    if os.path.exists(hotel_room_image_path):
        hotel_rooms_image = pd.read_csv(hotel_room_image_path, delimiter=',')
    else:
        print("Tệp tin 'image_room.csv' không tồn tại.")
        
    for room in listroom:
         # Kiểm tra xem DataFrame hotel_rooms_image có dữ liệu không
        if not hotel_rooms_image.empty:
            # Chọn ngẫu nhiên một dòng từ DataFrame hotel_rooms_image
            random_image_row = random.choice(hotel_rooms_image.index)
            random_image_link = hotel_rooms_image.loc[random_image_row, 'image']
        else:
            # Nếu DataFrame trống rỗng, sử dụng một liên kết hình ảnh mặc định
            random_image_link = 'default_image_link.jpg'

        # Gán random_image_link vào thuộc tính 'image' của room
        room['image'] = random_image_link
        room['isWishList'] = str(room['id']) in wishlist_items
        output.append(room)
    context = {'listroom': output}
    return render(request, 'hotel_detail.html', context)

def rate_hotel(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    if request.method == 'POST':
        hotel_id = request.POST.get('hotel_id')
        value = request.POST.get('value')
        user = UserProfile.objects.get(user=request.user)
        rating = Rating.objects.create(
            user=user,
            hotelID=hotel_id,
            value=value
        )
        return redirect('rating_list')
    return render(request, 'rate_hotel.html')

def rating_list(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    ratings = Rating.objects.all()
    return render(request, 'rating_list.html', {'ratings': ratings})

def testui(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    user_profile = UserProfile.objects.get(user=request.user) 
    # try:
    #     userPreferenceslist = UserPreferences.objects.filter(user=user_profile)
    # except ObjectDoesNotExist:
    #     userPreferenceslist = None 
    # if userPreferenceslist is not None:
    #     hotel_code_list = random_forest_based(userPreferenceslist[0].city, int(userPreferenceslist[0].number), userPreferenceslist[0].feature)
    #     hotel_code_list = random_forest_based(userPreferenceslist[1].city, int(userPreferenceslist[1].number), userPreferenceslist[1].feature) + hotel_code_list
    # else:
    #     city = 'london'
    #     number = 4
    #     features = 'I need a room with free wifi'
    #     hotel_code_list = random_forest_based(city, number, features)
    # hotel_list = get_hotels_data_by_codes(hotel_code_list)
    count = WishList.objects.filter(user=user_profile).count()   
    print(count)
    hotel_list = get_hotels_data_by_codes([31,97])
    new_hotel1 = get_hotel_list(1,5)
    new_hotel2 = get_hotel_list(5,9)
    trending1 = get_hotel_list(10,14)
    trending2 = get_hotel_list(14,18)
    context = {'newhotel1': new_hotel1,'newhotel2': new_hotel2,'trending1': trending1,'trending2': trending2, 'result': hotel_list, 'count': count}
    return render(request, 'home1.html', context)


def hotel_list(request,pagenumber):
    hotel_list = get_hotel_list(pagenumber*24,(pagenumber+1)*24)
    next = pagenumber +1
    prev = pagenumber -1
    context ={'hotelList' : hotel_list,'pageNumber': pagenumber, 'next' : next, 'prev' : prev}
    return render(request, 'hotel_list.html', context)

def hotelList(request,pagenumber):
    hotel_list = get_hotel_list(pagenumber*24,(pagenumber+1)*24)
    next = pagenumber +1
    prev = pagenumber -1
    context ={'hotelList' : hotel_list,'pageNumber': pagenumber, 'next' : next, 'prev' : prev}
    return render(request, 'hotellist.html', context)