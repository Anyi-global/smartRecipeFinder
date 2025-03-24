from app import app, mongo

from flask import render_template, request, url_for, redirect, flash, session, jsonify

from werkzeug.utils import secure_filename

from flask import send_from_directory, abort

from flask_mongoengine import MongoEngine

import bson.binary

import urllib.request

import os, re, requests

import datetime

from functools import wraps

# app.config = os.urandom(24)

app.config["SECRET_KEY"] = "b'n\x1d\xb1\x8a\xc0Jg\x1d\x08|!F3\x04P\xbf'"

app.config["UPLOAD_FOLDER"] = "/Users/ANYIGLOBAL/Desktop/MyProject/app/static/uploads"
app.config["ALLOWED_EXTENSIONS"] = ["TXT", "DOC", "PNG", "JPG", "JPEG", "GIF"]
app.config["CLIENT_IMAGES"] = "/Users/Anyiglobal/Desktop/MyProject/app/static/img/clients"

# Replace with your Edamam API ID and Key
EDAMAM_APP_ID = 'f1347fb1'
EDAMAM_APP_KEY = 'f9c7a54baf10512d0a42f5cc948e7a69'

def nigerian_time():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    today = datetime.date.today()
    d2 = today.strftime("%B %d, %Y")
    tm = now.strftime("%H:%M:%S %p")
    return (d2 +' '+'at'+' '+tm)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'login' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, Please login", 'danger')
            return redirect(url_for("index"))
    return wrap

@app.template_filter("clean_date")
def clean_date(dt):
    return dt.strftime("%d %b %Y")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You are successfully logged out!", 'success')
    return redirect(url_for("index"))

@app.route("/")
def index():
    return render_template("public/index.html")

@app.route("/register")
def register():
    return render_template("public/register.html")
    

@app.route("/users/dashboard")
@login_required
def users_dashboard():
    return render_template("public/users_portal.html")


@app.route("/all-given-assignments")
@login_required
def all_given_assignments():
    return render_template("public/view_all_given_assignments.html")

@app.route("/view-assignment-score")
@login_required
def view_assignment_score():
    return render_template("public/view_assignment_score.html")


@app.route('/recipe-search')
def recipe_search():
    return render_template('public/recipe_search.html')


@app.route('/search', methods=['POST'])
def search():
    ingredients = request.form['ingredients']
    dietary_preferences = request.form.getlist('preferences')

    # Construct the Edamam API URL
    api_url = 'https://api.edamam.com/search'
    params = {
        'q': ingredients,
        'app_id': EDAMAM_APP_ID,
        'app_key': EDAMAM_APP_KEY,
        'health': dietary_preferences
    }
    
    response = requests.get(api_url, params=params)
    data = response.json()

    return jsonify(data)
