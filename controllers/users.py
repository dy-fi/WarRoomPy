# from database import mongo
# from flask import Blueprint, render_template, abort, request
# from flask.ext.bcrypt import Bcrypt
# from flask_jwt_extended import (
#     JWTManager, jwt_required, create_access_token,
#     jwt_refresh_token_required, create_refresh_token,
#     get_jwt_identity, set_access_cookies,
#     set_refresh_cookies, unset_jwt_cookies
# )

# from auth import jwt

# db = mongo.db

# users_bp = Blueprint('users', __name__, template_folder='templates')

# class User():
#     def __init__(self, username, password, admin=False)
#         self.username = username
#         self.password = brcrypt.generate_password_hash(password)
    

# @users_bp.route('/login', methods=['POST'])
# def login():
#     if not request.is_json:
#         return jsonify({"msg": "Missing necessary request data"})
    
#     username = request.get("username")
#     password = request.get("password")

#     if not username:
#         return jsonify({"msg": "Missing username"})
#     if not password:
#         return jsonify({"msg": "Missing password"})
    
#     user = db.users.find('username':username)

#     if bcrypt.check_password_hash(user['password'], password):
#         access_token = create_access_token(identity=username)
#         refresh_token = create_refresh_token(identity=username)
#         resp = render_template("/rooms")
#         set_access_cookies(resp, access_token)
#         return resp
#     else:
#         return jsonify({"msg": "No users with those credentials were found"})


# @users_bp.route('/signup', methods=['POST'])
# def signup():
#     username = request.get("username")
#     password = request.get("password")

#     if not username:
#         return jsonify({"msg": "No username"})
#     if not password:
#         return jsonify({"msg": "No password"})

    