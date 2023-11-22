import numpy as np
import pandas as pd
import math,os,nltk, json
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize 
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# Initialize the TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer()
# Lấy đường dẫn của thư mục chứa script Python hiện tại
current_directory = os.getcwd()
# Đường dẫn tương đối đến các tệp tin CSV
hotel_rooms_path = os.path.join(current_directory, 'data-set', 'Hotel_Room_attributes.csv')
hotel_cost_path = os.path.join(current_directory, 'data-set', 'hotels_RoomPrice.csv')
hotel_details_path = os.path.join(current_directory, 'data-set', 'Hotel_details.csv')

# Kiểm tra xem các tệp tin tồn tại hay không và đọc chúng nếu tồn tại
if os.path.exists(hotel_rooms_path):
    hotel_rooms = pd.read_csv(hotel_rooms_path, delimiter=',')
else:
    print("Tệp tin 'Hotel_Room_attributes.csv' không tồn tại.")

if os.path.exists(hotel_cost_path):
    hotel_cost = pd.read_csv(hotel_cost_path, delimiter=',')
else:
    print("Tệp tin 'hotels_RoomPrice.csv' không tồn tại.")

if os.path.exists(hotel_details_path):
    hotel_details = pd.read_csv(hotel_details_path, delimiter=',')
else:
    print("Tệp tin 'Hotel_details.csv' không tồn tại.")

del hotel_details['id']
del hotel_rooms['id']
del hotel_details['zipcode']

# 3 dòng này chỉ chạy lần đầu
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

hotel_details=hotel_details.dropna()
hotel_rooms=hotel_rooms.dropna()
hotel_details.drop_duplicates(subset='hotelid',keep=False,inplace=True)
hotel=pd.merge(hotel_rooms,hotel_details,left_on='hotelcode',right_on='hotelid',how='inner')

# Chọn cột 'hotelid' và 'hotelname' từ bảng hotel
selected_hotel_columns = hotel_details[['hotelid', 'hotelname']]
# Merge bảng selected_hotel_columns và bảng hotel_cost
hotel_all = pd.merge(hotel_cost, selected_hotel_columns, left_on='hotelcode', right_on='hotelid', how='inner')

def citybased(city):
    hotel['city'] = hotel['city'].str.lower()
    citybase = hotel[hotel['city'] == city.lower()]
    citybase = citybase.sort_values(by='starrating', ascending=False)
    citybase.drop_duplicates(subset='hotelcode', keep='first', inplace=True)
    if not citybase.empty:
        hname = citybase[['hotelname', 'starrating', 'address', 'roomamenities', 'ratedescription']]
        result = hname.head().to_dict(orient='records')
        return json.dumps(result, ensure_ascii=False)
    else:
        return json.dumps({'error': 'No Hotels Available'}, ensure_ascii=False)

room_no=[
     ('king',2),
   ('queen',2), 
    ('triple',3),
    ('master',3),
   ('family',4),
   ('murphy',2),
   ('quad',4),
   ('double-double',4),
   ('mini',2),
   ('studio',1),
    ('junior',2),
   ('apartment',4),
    ('double',2),
   ('twin',2),
   ('double-twin',4),
   ('single',1),
     ('diabled',1),
   ('accessible',1),
    ('suite',2),
    ('one',2)
   ]
def calc():
    guests_no=[]
    for i in range(hotel.shape[0]):
        temp=hotel['roomtype'][i].lower().split()
        flag=0
        for j in range(len(temp)):
            for k in range(len(room_no)):
                if temp[j]==room_no[k][0]:
                    guests_no.append(room_no[k][1])
                    flag=1
                    break
            if flag==1:
                break
        if flag==0:
            guests_no.append(2)
    hotel['guests_no']=guests_no

calc()
hotel['roomamenities']=hotel['roomamenities'].str.replace(': ;',',')
def requirementbased(city,number,features):
    hotel['city']=hotel['city'].str.lower()
    hotel['roomamenities']=hotel['roomamenities'].str.lower()
    features=features.lower()
    features_tokens=word_tokenize(features)  
    sw = stopwords.words('english')
    lemm = WordNetLemmatizer()
    f1_set = {w for w in features_tokens if not w in sw}
    f_set=set()
    for se in f1_set:
        f_set.add(lemm.lemmatize(se))
    reqbased=hotel[hotel['city']==city.lower()]
    reqbased=reqbased[reqbased['guests_no']==number]
    reqbased=reqbased.set_index(np.arange(reqbased.shape[0]))
    l1 =[];l2 =[];cos=[];
    #print(reqbased['roomamenities'])
    for i in range(reqbased.shape[0]):
        temp_tokens=word_tokenize(reqbased['roomamenities'][i])
        temp1_set={w for w in temp_tokens if not w in sw}
        temp_set=set()
        for se in temp1_set:
            temp_set.add(lemm.lemmatize(se))
        rvector = temp_set.intersection(f_set)
        #print(rvector)
        cos.append(len(rvector))
    reqbased['similarity']=cos
    reqbased=reqbased.sort_values(by='similarity',ascending=False)
    reqbased.drop_duplicates(subset='hotelcode',keep='first',inplace=True)
    result = reqbased['hotelcode'].head(10).to_list()
    return result

def ratebased(city,number,features):
    hotel['city']=hotel['city'].str.lower()
    hotel['ratedescription']=hotel['ratedescription'].str.lower()
    features=features.lower()
    features_tokens=word_tokenize(features)  
    sw = stopwords.words('english')
    lemm = WordNetLemmatizer()
    f1_set = {w for w in features_tokens if not w in sw}
    f_set=set()
    for se in f1_set:
        f_set.add(lemm.lemmatize(se))
    rtbased=hotel[hotel['city']==city.lower()]
    rtbased=rtbased[rtbased['guests_no']==number]
    rtbased=rtbased.set_index(np.arange(rtbased.shape[0]))
    l1 =[];l2 =[];cos=[];
    
    for i in range(rtbased.shape[0]):
        temp_tokens=word_tokenize(rtbased['ratedescription'][i])
        temp1_set={w for w in temp_tokens if not w in sw}
        temp_set=set()
        for se in temp1_set:
            temp_set.add(lemm.lemmatize(se))
        rvector = temp_set.intersection(f_set)
        
        cos.append(len(rvector))
    rtbased['similarity']=cos
    rtbased=rtbased.sort_values(by='similarity',ascending=False)
    rtbased.drop_duplicates(subset='hotelcode',keep='first',inplace=True)
    result = rtbased['hotelcode'].head(10).to_list()
    return result

def random_forest_based(city, number, features):
    hotel['city'] = hotel['city'].str.lower()
    hotel['roomamenities'] = hotel['roomamenities'].str.lower()
    features = features.lower()
    # Lọc dữ liệu theo city và số lượng khách cần
    rf_data = hotel[(hotel['city'] == city.lower()) & (hotel['guests_no'] == number)]
    # rf_data = hotel_all
    if not rf_data.empty:
        # Tạo dữ liệu huấn luyện
        X = tfidf_vectorizer.fit_transform(rf_data['roomamenities'])  # Ma trận TF-IDF
        y = rf_data['hotelcode']  # Nhãn (hotelcode)
        # Chia dữ liệu thành tập huấn luyện và tập kiểm tra
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        # Tạo và huấn luyện mô hình Random Forest
        rf_model = RandomForestClassifier()
        rf_model.fit(X_train, y_train)
        # Dự đoán trên tập kiểm tra
        y_pred = rf_model.predict(X_test)
        # Tính độ chính xác
        accuracy = accuracy_score(y_test, y_pred)
        print("Accuracy:", accuracy)
        # Biến đổi các features theo TF-IDF
        features_tfidf = tfidf_vectorizer.transform([features])
        # Dự đoán khách sạn dựa trên features
        predictions = rf_model.predict(features_tfidf)
        predicted_hotels = rf_data[rf_data['hotelcode'].isin(predictions)]
        if not predicted_hotels.empty:
            predicted_hotels.drop_duplicates(subset='hotelcode', keep='first', inplace=True)
            # result = predicted_hotels[['city', 'hotelname', 'roomtype', 'guests_no', 'starrating', 'address', 'roomamenities', 'ratedescription']].head(10).to_dict(orient='records')
            result = predicted_hotels['hotelcode'].tolist()
            print(result)
            return result
        else:
            return []
    else:
        return []
     
    #     if not predicted_hotels.empty:
    #         # predicted_hotels = predicted_hotels.sort_values(by='similarity', ascending=False)
    #         predicted_hotels.drop_duplicates(subset='hotelcode', keep='first', inplace=True)
    #         result = predicted_hotels[['city', 'hotelname', 'roomtype', 'guests_no', 'starrating', 'address', 'roomamenities', 'ratedescription']].head(10).to_dict(orient='records')
    #         print(result)
    #         return json.dumps(result, ensure_ascii=False)
    #     else:
    #         return json.dumps({'error': 'No Hotels Available based on given features'}, ensure_ascii=False)
    # else:
    #     return json.dumps({'error': 'No Hotels Available for the specified city and number of guests'}, ensure_ascii=False)


