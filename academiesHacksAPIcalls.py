import requests
import datetime
import time
import json

#Date and time
today = datetime.date.today()
timestamp = str(int(time.mktime(today.timetuple())))
print("date: " + str(today))

#static latitude and longitude
lat = -9
lng = -72
print("lat: " + str(lat) + ", lng: " + str(lng))

#json method
def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    return(text)


#call API for temperature and humidity
response = requests.get("https://api.openweathermap.org/data/2.5/onecall/timemachine?lat=" + str(lat) + "&lon=" + str(lng) + "&units=metric&dt=" + str(int(timestamp)) + "&appid=7027ad30a8416cdfdb806d56fbf542e0")
jsonguy = response.json()
humidity = jsonguy["current"]["humidity"]
print("humidity: " + str(humidity))
temp = jsonguy["current"]["temp"]
print("temp: " + str(temp))

#call API for Soil pH
responseTwo = requests.get("https://rest.soilgrids.org/soilgrids/v2.0/properties/query?lon=" + str(lng) + "&lat=" + str(lat) + "&property=phh2o&depth=0-5cm&value=mean")
responseTwo = responseTwo.json()
soilPH = responseTwo["properties"]["layers"][0]["depths"][0]["values"]["mean"]
if soilPH != None:
    soilPH = float(soilPH / 10)
else:
    soilPH = "None"
print("soil pH: " + str(soilPH))

#call for API for Soil Moisture
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
    'Authorization': '3bf58956-c113-11eb-8d12-0242ac130002-3bf589f6-c113-11eb-8d12-0242ac130002'
  }
)
responseThree = response1.json()
soilMoisture = responseThree["hours"][0]["soilMoisture"]['noaa']
print("soil moisture: " + str(soilMoisture))
