from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['EDAMAM_API_ID'] = os.getenv('EDAMAM_API_ID')
app.config['EDAMAM_API_KEY'] = os.getenv('EDAMAM_API_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')

#app configuration
app_settings = os.environ.get(
    'APP_SETTINGS'
    'app.config'
) 
app.config.from_object(app_settings)

#initializing PyMongo
mongo = PyMongo(app, app.config['MONGO_URI'])

from app import views
