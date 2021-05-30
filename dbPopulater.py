from pymongo import MongoClient

client = MongoClient("mongodb+srv://AvyukthN:Night04Monkey$@onlypotatoes.ds56j.mongodb.net/OnlyPotatoes?retryWrites=true&w=majority")

db = client.farmdata

dataObjs = db.dataObjs

query_filter = {'latitude': '37.0902'}

dataObjs.delete_many(query_filter)


"""
dataObjs.inventory.deleteMany({
        'latitude': '37.0902',
        'longitude': '-95.7129',
        'temperature': '45',
        'ph': 'awefawe f',
        'humidity': '23%',
        'soil_mositure': 'sadfasfd'
    })
"""

"""
db.invoice.delete_many({
        latitude: '37.0902',
        longitude: '-95.7129',
        temperature: '45',
        ph: 'awefawe f',
        humidity: '23%',
        soil_mositure: 'sadfasfd'
    })
"""
