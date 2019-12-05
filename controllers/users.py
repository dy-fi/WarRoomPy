from database import mongo
from auth import auth

from flask import Blueprint, render_template, request, jsonify, current_app, make_response, redirect, url_for,jsonify
from flask_bcrypt import Bcrypt
from bson import ObjectId, json_util
from flask_httpauth import HTTPBasicAuth
import json

from models.user import User


db = mongo.db
users_bp = Blueprint('users', __name__, template_folder='templates')

bcrypt = Bcrypt(current_app)

def validate_login(password_hash, password):
    return bcrypt.check_password_hash(password_hash, password)


@auth.verify_password
def verify_password(username, password):
    user = db.users.find_one({'username' : username})
    return validate_login(user['password'], password)

@users_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("error.html", err="We need both a username and password")
        
        # database entry
        user = db.users.find_one({'username': username })

        if not user:
            return render_template("error.html", err="No users with those credentials were found")

        if validate_login(user['password'], password):
            
            return redirect(url_for("target.show_rooms"))
        else:
            return render_template("error.html", err="No users with those credentials were found")


@users_bp.route('/sign-up', methods=['GET', 'POST'])
def signup():

    if request.method == 'GET':
        return render_template('sign-up.html')

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("error.html", err="We need both a username and password")
        
        # will be 1 if that username already exists, 0 otherwise
        users = db.users.find({ 'username': username }).limit(1).count()

        if users == 1:
            return render_template("error.html", err="Someone already has that username")

        hashed_password = bcrypt.generate_password_hash(password)

        newUser = {
            'username': username,
            'password': hashed_password,
            'targets': [],
            'banned': False,
            'admin': False,
        }

        db.users.insert_one(newUser)
        user_model = User(username)
        
        return redirect(url_for("index.index"))
        

@users_bp.route('/logout', methods=['GET'])
@login_required
def logout():
 
   return redirect(url_for("index.index"))