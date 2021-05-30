import csv
from pymongo import MongoClient

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
