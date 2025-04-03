from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/")
    print("Connected to MongoDB successfully!")
    print("Available Databases:", client.list_database_names())  # List databases if connected
except Exception as e:
    print("Error connecting to MongoDB:", e)
