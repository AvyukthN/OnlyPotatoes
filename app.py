from flask import Flask, render_template, request, redirect, url_for
import smtplib
from pymongo import MongoClient
import requests
import datetime
import time
import json
from bs4 import BeautifulSoup
from math import sin, cos, sqrt, atan2, radians
import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans

client = MongoClient("mongodb+srv://AvyukthN:Night04Monkey$@onlypotatoes.ds56j.mongodb.net/OnlyPotatoes?retryWrites=true&w=majority")

db = client.farmdata
db2 = client.cropdata

dataObjs = db.dataObjs
crObjs = db2.crObjs

def KMEANS():
    client = MongoClient("mongodb+srv://AvyukthN:Night04Monkey$@onlypotatoes.ds56j.mongodb.net/OnlyPotatoes?retryWrites=true&w=majority")

    db = client['cropdata']
    collection = db['crObjs']

    data_points = []

    for post in collection.find():
        data_points.append([post['latitude'], post['longitude'], post['crop-type']])

    print(data_points)

    with open('datapoints.csv', 'w') as f:
        dwriter = csv.writer(f, delimiter = ',')
        
        dwriter.writerow(['longitude', 'latitude', 'crop_type'])
        for i in range(len(data_points)):
            lat = data_points[i][1]
            lng = data_points[i][0]
            crtype = data_points[i][2] 
            
            dwriter.writerow([lng, lat, crtype])

    dataset = pd.read_csv('datapoints.csv')
    X = dataset.iloc[:, [0,1]].values

    kmeans = KMeans(n_clusters = 5, init = 'k-means++', random_state = 42)
    y_kmeans = kmeans.fit_predict(X)
    
    return (kmeans.cluster_centers_)

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    return(text)

def populateDB(latitude, longitude, temp, ph, humidity, soil_moisture):
    ObjsDoc = {
            "latitude": latitude,
            "longitude": longitude,
            "temperature": temp,
            "ph": ph,
            "humidity": humidity,
            "soil_mositure": soil_moisture
            }

    dataObjs.insert_one(ObjsDoc)

def populateDB2(latitude, longitude, crop_type):
    ObjsDoc = {
            "crop-type": crop_type,
            "latitude": latitude,
            "longitude": longitude,
            }

    crObjs.insert_one(ObjsDoc)

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        dat_hashmap = {}

        for key, value in request.form.items():
            if key == 'type':
                crop_type = value
            if key == 'location':
                coords = value
                coords = coords.split(",")
                dat_hashmap.update({'location': coords})
                
                lat = float(coords[0])
                lng = float(coords[1])

                today = datetime.date.today()
                timestamp = str(int(time.mktime(today.timetuple())))

                response = requests.get("https://api.openweathermap.org/data/2.5/onecall/timemachine?lat=" + str(lat) + "&lon=" + str(lng) + "&units=metric&dt=" + str(int(timestamp)) + "&appid=7027ad30a8416cdfdb806d56fbf542e0")
                jsonguy = response.json()
                humidity = jsonguy["current"]["humidity"]
                temp = jsonguy["current"]["temp"]

                responseTwo = requests.get("https://rest.soilgrids.org/soilgrids/v2.0/properties/query?lon=" + str(lng) + "&lat=" + str(lat) + "&property=phh2o&depth=0-5cm&value=mean")
                responseTwo = responseTwo.json()
                soilPH = responseTwo["properties"]["layers"][0]["depths"][0]["values"]["mean"]
                if soilPH != None:
                    soilPH = float(soilPH / 10)
                else:
                    soilPH = "None"

                response1 = requests.get(
                  'https://api.stormglass.io/v2/bio/point',
                  params={
                    'lat': lat,
                    'lng': lng,
                    'params': 'soilMoisture',
                    'start': timestamp,
                    'end': timestamp
                  },
                  headers={
                    'Authorization': '0b0c7be8-c13a-11eb-80ed-0242ac130002-0b0c7c74-c13a-11eb-80ed-0242ac130002'

                  }
                )
                responseThree = response1.json()
                print(responseThree["hours"])
                try:
                    soilMoisture = responseThree["hours"][0]["soilMoisture"]['noaa']
                except:
                    pass

                dat_hashmap.update({'humidity': humidity})
                dat_hashmap.update({'temperature': temp})
                dat_hashmap.update({'ph': soilPH})
                dat_hashmap.update({'soil_moisture': soilMoisture})

            if key == 'KMEANS':
                centroids = KMEANS()
                toparse = ""
                for coord in centroids:
                    for part in coord:
                        toparse += str(part)
                        toparse += "$"
                    toparse += ","
                print(toparse)
                context = {"data3": toparse}
                return render_template('home.html', **context)

        if crop_type == "potato":
            populateDB(dat_hashmap['location'][0], dat_hashmap['location'][1], dat_hashmap['temperature'], dat_hashmap['ph'], dat_hashmap['humidity'], dat_hashmap['soil_moisture'])

        populateDB2(dat_hashmap['location'][0], dat_hashmap['location'][1], crop_type)

        arrDicts = []
        arrDicts2 = []

        db = client['farmdata']
        collection = db['dataObjs']
        db2 = client['cropdata']
        collection2 = db2['crObjs']
        
        for post in collection.find():
            arrDicts.append(post)
        for post in collection2.find():
            arrDicts2.append(post)

        """
        $.ajax({
            url: "/",
            type = "POST",
            async = false,
            data:{
                data_objs:arrDicts,
            },
            success: function(response){
                console.log("Data Recieved");
                console.log(response);
            },
            error: function(response){
                console.log("error");
                console.log(response);
            }
        });
        """
        
        toparse = ""
        for hashmap in arrDicts:
            print(hashmap)
            for data_obj in hashmap:
                if data_obj != '_id':
                    toparse += str(hashmap[data_obj])
                    toparse += "$"
            toparse += ","

        toparse2 = ""
        for hashmap in arrDicts2:
            for data_obj in hashmap:
                if data_obj != '_id':
                    toparse2 += str(hashmap[data_obj])
                    toparse2 += "$"
            toparse2 += ","

        final_message = ""

        def MLPOTATOES(temp, ph, humdity, moisture):
          final_message = ""
          count = 0
          if(temp>45 and temp<104.5): count+=1
          else: final_message += "Temperature is not ideal"
          if(ph>4.5 and ph<7.7): count+=1
          else: final_message += "\npH is not ideal"
          if(humidity>85.5): count+=1
          else: final_message += "\nHumidity is not suitable"
          if(moisture> 0.72 and moisture< 0.99): count+=1
          else: final_message += "\nToo much or too little moisture"
          
          if count !=4: 
            return_arr = [False, final_message]
            return return_arr 
          
          return_arr = [True, "DUMMY"]
          return return_arr 
        
        potato_bool, final_message = MLPOTATOES(float(dat_hashmap['temperature']), float(dat_hashmap['ph']), float(dat_hashmap['humidity']), float(dat_hashmap['soil_moisture']))
        
        if final_message != "":
            context = {
                    'data': toparse,
                    'latitude': dat_hashmap['location'][0],
                    'longitude': dat_hashmap['location'][1],
                    'temperature': dat_hashmap['temperature'],
                    'ph': dat_hashmap['ph'],
                    'humidity': dat_hashmap['humidity'],
                    'soil_moisture': dat_hashmap['soil_moisture'],
                    'potato_bool': potato_bool,
                    'final_message': final_message
            }
        else:
            context = {
                    'data': toparse,
                    'latitude': dat_hashmap['location'][0],
                    'longitude': dat_hashmap['location'][1],
                    'temperature': dat_hashmap['temperature'],
                    'ph': dat_hashmap['ph'],
                    'humidity': dat_hashmap['humidity'],
                    'soil_moisture': dat_hashmap['soil_moisture'],
                    'potato_bool': potato_bool
            }

        context.update({"data": toparse, "data2": toparse2})


        if context['latitude']:
            return render_template('home.html', **context)
        
        return render_template('home.html', {"data": toparse, "data2": toparse2}) 

    if request.method == 'GET':
        arrDicts = []
        arrDicts2 = []

        db = client['farmdata']
        db2 = client['cropdata']
        collection = db['dataObjs']
        collection2 = db2['crObjs']
        
        for post in collection.find():
            arrDicts.append(post)
        for post in collection2.find():
            arrDicts2.append(post)

        length = len(arrDicts)

        print(arrDicts)
        print("\n")

        values = arrDicts
        values2 = arrDicts2

        """
        $.ajax({
            url: "/",
            type = "POST",
            async = false,
            data:{
                data_objs:arrDicts,
            },
            success: function(response){
                console.log("Data Recieved");
                console.log(response);
            },
            error: function(response){
                console.log("error");
                console.log(response);
            }
        });
        """
        
        toparse = ""
        for hashmap in arrDicts:
            print(hashmap)
            for data_obj in hashmap:
                if data_obj != '_id':
                    toparse += str(hashmap[data_obj])
                    toparse += "$"
            toparse += ","

        toparse2 = ""
        for hashmap in arrDicts2:
            for data_obj in hashmap:
                if data_obj != '_id':
                    toparse2 += str(hashmap[data_obj])
                    toparse2 += "$"
            toparse2 += ","

        print(toparse)

        context = {"data": toparse, "data2": toparse2}

        return render_template('home.html', **context)

@app.route('/heatmap', methods = ['GET', 'POST'])
def heatmap():
    arrDicts = []

    db = client['cropdata']
    collection = db['crObjs']
    
    for post in collection.find():
        arrDicts.append(post)

    length = len(arrDicts)

    print(arrDicts)
    print("\n")

    values = arrDicts
    
    toparse = ""
    for hashmap in arrDicts:
        print(hashmap)
        for data_obj in hashmap:
            if data_obj != '_id':
                toparse += str(hashmap[data_obj])
                toparse += "$"
        toparse += ","

    print(toparse)

    context = {"data": toparse}

    return render_template('heatmap.html', **context) 

@app.route('/distance', methods = ['GET', 'POST'])
def dist():
    if request.method == 'POST':
        for key, value in request.form.items():
            if key == 'coord1':
                coord1 = value
            if key == 'coord2':
                coord2 = value
            if key == 'planet':
                planet = value
        if coord1:     
            R = 6373.0
            latitude1 = float(coord1.split(",")[0])
            longitude1 = float(coord1.split(",")[1]) 
            latitude2 = float(coord2.split(",")[0])
            longitude2 = float(coord2.split(",")[1])

            lat1 = radians(latitude1)
            lon1 = radians(longitude1)
            lat2 = radians(latitude2)
            lon2 = radians(longitude2)

            dlon = lon2 - lon1
            dlat = lat2 - lat1

            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance = R * c
            potatoLength = 7.9375/100000

            potatoDistance = int(distance/potatoLength)

            potatoDistance = str(potatoDistance) + " POTATOES"
        elif planet:
            planet = planet.capitalize()
            potatoDistance = ""
            if(planet == "Mercury"):
                potatoDistance = "729,907,200,000 POTATOES"
            elif(planet == "Venus"):
                potatoDistance = "527,155,200,000 POTATOES"
            elif(planet == "Sun"):
                potatoDistance = "1,910,552,400,000 POTATOES"
            elif(planet == "Mars"):
                potatoDistance = "9,075,990,500,000 POTATOES"
            elif(planet == "Jupiter"):
                potatoDistance = "9,075,990,500,000 POTATOES"
            elif(planet == "Saturn"):
                potatoDistance = "15,125,299,000,000 POTATOES"
            elif(planet == "Uranus"):
                potatoDistance = "389,223,010,000,000 POTATOES"
            elif(planet == "Neptune"):
                potatoDistance = "568,232,760,000,000 POTATOES"
            else:
                potatoDistance = "That's not a planet!"

        context = {'distance': potatoDistance}

        return render_template('dist.html', **context)

    return render_template('dist.html')

@app.route('/price', methods = ['GET', 'POST'])
def price():
    if request.method == 'POST':
        for key, value in request.form.items():
            if key == 'url':
                URL = value
        HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

        webpage = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(webpage.content, "lxml")

        def get_price(soup):
            try:
                price = soup.find("span", attrs={'class':'price-characterisitic'}).string.strip()
            except AttributeError:
                try:
                    # If there is some deal price
                    price = soup.find("span", attrs={'class':'price-characteristic'}).string.strip()
                except:     
                    price = ""  
            return price
        price = get_price(soup)
        price = (float(price)/.25)
        
        replacSTR = "It takes {} Potatoes to buy that!".format(price)

        if price:
            return render_template('price.html', pricePot = replacSTR)

    welcomeSTR = "Enter a url for an amazon product to see how much it costs in potatoes!"

    return render_template('price.html', pricePot = welcomeSTR)

if __name__ == '__main__':
    app.run(debug = True)
