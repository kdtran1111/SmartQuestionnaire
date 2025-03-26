# this file handles the mongodb connection to the flask site
from pymongo import MongoClient

# MongoDB connection string
client = MongoClient("mongodb+srv://kdtran1111:Danh.2001@cluster0.uz0bc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Database and collection references
db = client["questionnaire_db"]
responsesCol = db["responses"]
questionnaireCol = db["questions"]
usersCol = db["users"]
