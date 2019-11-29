from database import mongo
from flask import Blueprint, render_template, request, jsonify, current_app, make_response, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies, get_raw_jwt
)

db = mongo.db
users_bp = Blueprint('users', __name__, template_folder='templates')

jwt = JWTManager(current_app)
bcrypt = Bcrypt(current_app)

# blacklist
blacklist = set()

def _authenticate(username, url):
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    resp = make_response(redirect(url_for(url)))
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp

# blacklist for logout
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist
    
@users_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("error.html", err="We need both a username and password")
        
        user = db.users.find_one({'username': username })

        if not user:
            return render_template("error.html", err="No users with those credentials were found")

        if bcrypt.check_password_hash(user['password'], password):
            return _authenticate(username, "target.show_rooms")
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
            'admin': False
        }

        db.users.insert_one(newUser)

        return _authenticate(username, "target.show_rooms")

@users_bp.route('/logout', methods=['GET'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return render_template("index.html")

