import pandas as pd
import csv
import os
import json

current_directory = os.getcwd()
hotel_cost_path = os.path.join(current_directory, 'data-set', 'hotels_RoomPrice.csv')
hotel_details_path = os.path.join(current_directory, 'data-set', 'Hotel_details.csv')

# Kiểm tra xem các tệp tin tồn tại hay không và đọc chúng nếu tồn tại
hotel_info_path = os.path.join(current_directory, 'data-set', 'Hotel.csv')
hotel_price_average_path = os.path.join(current_directory, 'data-set', 'HotelPriceSummary.csv')
if os.path.exists(hotel_info_path):
    hotel_info = pd.read_csv(hotel_info_path, delimiter=',')
else:
    print("Tệp tin 'Hotel.csv' không tồn tại.")
if os.path.exists(hotel_price_average_path):
    hotel_price_average = pd.read_csv(hotel_price_average_path, delimiter=',')
else:
    print("Tệp tin 'HotelPriceSummary.csv' không tồn tại.")


def get_hotels_data_by_codes(hotel_codes):
    filtered_rows = hotel_price_average[hotel_price_average['hotelcode'].isin(hotel_codes)].to_dict(orient='records')
    return filtered_rows

def get_room_in_hotel(hotel_code):
    filtered_rows = hotel_info[hotel_info['hotelcode']==hotel_code]
    list_room = filtered_rows[['id','roomtype','onsiterate','ratedescription']].to_dict(orient='records')
    return list_room

def get_hotelcode_by_room(roomid):
    filtered_rows = hotel_info[hotel_info['id']==roomid]
    hotelId = filtered_rows['hotelcode'].to_list()
    rs = hotelId[0]
    return rs

def getUserPreferencesByRoom(roomid):
    hotel_price_average['city'] = hotel_price_average['address'].str.split(',').str[1].str.strip()
    filtered_rows = hotel_info[hotel_info['id']==roomid]
    number = filtered_rows['maxoccupancy'].to_list()
    feature = filtered_rows['roomamenities'].to_list()
    filtered = hotel_price_average[hotel_price_average['hotelcode']==get_hotelcode_by_room(roomid)]
    city = filtered['city'].to_list()
    (city[0],feature[0].replace(': ;',', '),number[0])
    rs =[city[0],int(number[0]),feature[0].replace(': ;',', ')]
    return rs

def get_hotel_list( begin, end):
    filtered = hotel_price_average.iloc[begin:end].to_dict(orient='records')
    return filtered

def get_hotel_by_name(hotlename):
    hotlename = hotlename.lower()
    filtered_rows = hotel_price_average[hotel_price_average['hotelname'].str.contains('a')]
    hotelId = filtered_rows['hotelcode'].to_list()
    rs = hotelId[0]
    return rs