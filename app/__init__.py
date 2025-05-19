from flask import Flask
from flask_pymongo import PyMongo
# from pymongo import MongoClient
# import certifi
from dotenv import load_dotenv # type: ignore
import os

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['EDAMAM_API_ID'] = os.getenv('EDAMAM_API_ID')
app.config['EDAMAM_API_KEY'] = os.getenv('EDAMAM_API_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')

#initializing PyMongo
mongo = PyMongo(app)

'''
This is a solution for MAC OS Mongodb certificate issue

# ca = certifi.where()
# client = MongoClient(app.config['MONGO_URI'], tlsCAFile=ca)
# # mongo = client.get_default_database()
# mongo = client["RecipeFinderApp"]
'''

from app import views
