import csv
from pymongo import MongoClient
import random

client = MongoClient("mongodb+srv://AvyukthN:Night04Monkey$@onlypotatoes.ds56j.mongodb.net/OnlyPotatoes?retryWrites=true&w=majority")

db = client.cropdata

crObjs = db.crObjs

pot_coords = [[37.090, -95.72]]
sugar_coords = [[-9, -72]]
rice_coords = [[20.5937, 78.9629]]
maize_coords = [[14.2350, 51.9253]]
corn_coords = [[46.2276, 2.2137]]
wheat_coords = [[-82.8628, 135.0]]

full_arr = [pot_coords, sugar_coords, rice_coords, maize_coords, corn_coords, wheat_coords]

for arr in full_arr:
    for i in range(10):
        adder = random.randint(-2, 2)
        sec_adder = random.randint(-2, 2)
        last_index = len(arr) - 1
        prev = arr[last_index]

        arr.append([prev[0] + adder, prev[1] + adder])
        arr.append([prev[0] - adder, prev[1] + adder])


for i in range(len(full_arr)):
    if i == 0:
        crtype = "potato"
    if i == 1:
        crtype = "sugar"
    if i == 2:
        crtype = "rice"
    if i == 3:
        crtype = "maize"
    if i == 4:
        crtype = "corn"
    if i == 5:
        crtype = "wheat"
    for j in range(len(full_arr[i])):
        data_doc = {
                "crop-type": crtype,
                "latitude": full_arr[i][j][0],
                "longitude": full_arr[i][j][1]
        }
        
        crObjs.insert_one(data_doc)
