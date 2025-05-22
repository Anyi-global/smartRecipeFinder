from app import app, mongo
from flask import render_template, request, url_for, redirect, flash, session, jsonify
from werkzeug.utils import secure_filename
from flask import send_from_directory, abort
from flask_mongoengine import MongoEngine
import bson.binary
import urllib.request
import os, re, requests
import datetime
import pytz
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# app.config = os.urandom(24)

# app.config["SECRET_KEY"] = "b'n\x1d\xb1\x8a\xc0Jg\x1d\x08|!F3\x04P\xbf'"

def finnish_time():
    '''
    This function extracts
    the current Finnish time
    '''
    # Define Finnish timezone
    helsinki = pytz.timezone('Europe/Helsinki')
    
    # Get current time in Finnish timezone
    now = datetime.datetime.now(helsinki)
    today = now.date()
    
    d2 = today.strftime("%B %d, %Y")
    tm = now.strftime("%H:%M:%S:%p")
    
    return f"{d2} at {tm}"

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

# home endpoint
@app.route("/")
def index():
    return render_template("public/index.html")

# signup endpoint
@app.route("/register")
def register():
    return render_template("public/register.html")

# user dashbord endpoint
    

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


@app.route('/api/search-recipe', methods=['POST'])
def search():
    ingredients = request.form['ingredients'].lower()
    dietary_preferences = request.form.getlist('preferences')
    cuisine_type = request.form.get('cuisineType').lower()  # Get the selected cuisine type

    # Ensure ingredients are provided
    if not ingredients:
        return jsonify({"error": "Please enter ingredients to search."}), 400

    # Edamam API URL
    api_url = 'https://api.edamam.com/api/recipes/v2'
    params = {
        'q': ingredients,
        'app_id': os.getenv('EDAMAM_API_ID'),
        'app_key': os.getenv('EDAMAM_API_KEY'),
        'type': 'public'
    }

    # Add dietary preferences (if any)
    for pref in dietary_preferences:
        params.setdefault('health', []).append(pref.lower())

    # Add cuisine type if provided    
    if cuisine_type:
        params['cuisineType'] = cuisine_type

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.JSONDecodeError:
        print("JSON decode error - raw response:", response.text)
        return jsonify({"error": "Failed to decode JSON response from Edamam API."})
    except requests.exceptions.RequestException as e:
        print("Request failed:", str(e))
        return jsonify({"error": "Failed to fetch data from Edamam API."})

# SignUp EndPoint
@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method=='POST':
        req = request.form
        
        username = str(req["username"])
        email = str(req["email"]).lower()
        password = req["pswd"]
        con_password = req["con_pswd"]
        
        if password != con_password:
            flash("Password Confirmation Mismatched, Please Confirm Your Password!", "danger")
            return render_template("public/register.html")
        # checkuser = mongo.db.sign_up.find_one({"matric_number":mat_no}, {"_id":0})
        checkuser = mongo.db.signup.find_one({"username": username}, {"_id":0})
        if checkuser:
            flash("Sorry, User already registered!", "danger")
            return render_template("public/register.html")
        # checkemail = mongo.db.sign_up.find_one({"email":email}, {"_id":0})
        checkemail = mongo.db.signup.find_one({"email": email}, {"_id":0})
        if checkemail:
            flash("Sorry, User with email address already exists!", "danger")
            return render_template("public/register.html")

        hashed_password = generate_password_hash(password)
        
        mongo.db.signup.insert_one({"username": username, "email": email, "password": hashed_password, "activationStatus":"0", "registeredDate": finnish_time()})
        flash("Account Created Successfully!", "success")
        return redirect(url_for("index"))
    else:
        return render_template("public/register.html")

# Login EndPoint
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=='POST':
        req = request.form
        
        username = str(req["username"])
        pswd = req["pswd"]
        
        checkuser = mongo.db.signup.find_one({"username": username}, {"_id":0})
        
        # x = re.search(pattern, string)
        
        if not checkuser:
            flash("Username/Password Incorrect!", "danger")
            return render_template("public/index.html")
        
        # elif checkuser["activationStatus"] != "1":
        #     flash("Account not activated. Contact Admin for account activation!", "danger")
        #     return render_template("public/index.html")
        
        if not check_password_hash(checkuser["password"], pswd):
            flash("Username/Password Incorrect!", "danger")
            return render_template("public/index.html")
                  

        del checkuser["password"]
        session["user"] = checkuser
        session["login"]=True

        # if checkuser["username"] == "admin":
        #     flash("Logged in Successfully! Welcome to your Dashboard!!", "success")
        #     return redirect(url_for("admin_dashboard"))
            
        # else:
        flash("Logged in Successfully! Welcome to your Dashboard!!", "success")
        return redirect(url_for("users_dashboard"))
    
    return render_template("public/index.html")

# Edit Profile EndPoint (though not neccessary for this project)
@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method=='POST':
        req = request.form
        print(req)
    
        username = req["username"]
        new_email = req["email"]
    
        # checkuser = mongo.db.sign_up.find_one({"matric_number":mat_no}, {"_id":0})
        checkuser = mongo.db.signup.find_one({username:{"$exists":True}}, {"_id":0})
        if not checkuser:
            flash("Sorry, User not registered!", "danger")
            return render_template("public/student_profile.html")
        # checkemail = mongo.db.sign_up.find_one({"email":email}, {"_id":0})
        checkemail = mongo.db.signup.find_one({new_email:{"$exists":True}}, {"_id":0})
        if checkemail:
            flash("Sorry, User with email address already exists!", "danger")
            return render_template("public/student_profile.html")
    
        old_email = checkuser["email"]
        # mongo.db.sign_up.update_one({mat_no:{"$exists":True}}, {"$unset": {"email": old_email,:new_email}})
        mongo.db.signup.update_one({username:{"$exists":True}}, {"$set": {"email": new_email}, "$unset": {old_email: ""}})
        flash("Profile Updated Successfully!", "success")
        return redirect(url_for("student_profile"))
    
    return render_template("public/student_profile.html")

# Change Password EndPoint (though not neccessary for this project)
@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method=='POST':
        req = request.form
    
        currentpswd = req["currentpassword"]
        newpswd = req["newpassword"]
        renewpswd = req["renewpassword"]
    
        # checkuser = mongo.db.sign_up.find_one({"matric_number":mat_no}, {"_id":0})
        checkpassword = mongo.db.signup.find_one({currentpswd:{"$exists":True}}, {"_id":0})
        if not checkpassword:
            flash("Sorry, Incorrect Password", "danger")
            return render_template("public/student_profile.html")
        # checkemail = mongo.db.sign_up.find_one({"email":email}, {"_id":0})
        if newpswd == currentpswd:
            flash("Sorry, Current password and New password must be different!", "danger")
            return render_template("public/student_profile.html")
        if newpswd != renewpswd:
            flash("New password do not match!", "danger")
            return render_template("public/student_profile.html")
        # checkemail = mongo.db.signup.find_one({new_email:{"$exists":True}}, {"_id":0})
        # if checkemail:
        #     flash("Sorry, User with email address already exists!", "danger")
        #     return render_template("public/student_profile.html")
        
        old_pswd = checkpassword['password']
        # mongo.db.sign_up.update_one({mat_no:{"$exists":True}}, {"$unset": {"email": old_email,:new_email}})
        mongo.db.signup.update_one({currentpswd:{"$exists":True}}, {"$set": {"password": newpswd}, "$unset": {old_pswd: ""}})
        flash("Password Changed Successfully!", "success")
        return redirect(url_for("student_profile"))
    
    return render_template("public/student_profile.html")
