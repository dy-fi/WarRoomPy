import gevent
from gevent import monkey;
monkey.patch_all()

from flask import Flask
from flask import render_template, url_for
from flask_cors import CORS
# from flask.ext.bcrypt import Bcrypt
from flask_socketio import SocketIO, send, emit
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)




from bson import ObjectId
import time
import datetime 
import json
import re
import os
import logging

from database import mongo
import scrapper

# ==============Server Init================

app = Flask(__name__)


logging.getLogger('flask_cors').level = logging.DEBUG

# config
app.config.from_pyfile("config.cfg")
app.config["SECRET_KEY"] = os.environ.get("SECRET", 'not the real secret lol')
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", 'not the real secret lol')
app.config["JWT_COOKIE_CSRF_PROTECT"] = True
app.config['JWT_TOKEN_LOCATION'] = ['cookies']

# switch in production
app.config["JWT_COOKIE_SECURE"] = False
app.config["DEBUG"] = True

# ==================DB=====================

port = int(os.environ.get("PORT", 5000))
 
app.config["MONGO_URI"] = "mongodb://localhost:27017/wrdb"
# app.config["MONGO_URI"] = "mongodb://heroku_r6c7r7n3:ruhocdtre5vj1bt4cf5bjep29j@ds237308.mlab.com:37308/heroku_r6c7r7n3?retryWrites=false"
mongo.init_app(app)

db = mongo.db


# ==============Middleware=================

# jwt wrapper
jwt = JWTManager(app)

# enable CORS
CORS(app)

# # bcrypt
# bcrypt = Bcrypt(app)

# ================Routes===================

from controllers.index import index_bp
from controllers.places import place_bp
from controllers.sockets import socket_bp
from controllers.targets import target_bp

app.register_blueprint(index_bp)
app.register_blueprint(place_bp)
app.register_blueprint(socket_bp)
app.register_blueprint(target_bp)

# ================Sockets==================


io = SocketIO(app, async_mode="gevent", manage_session=False)
clients = {}
interval = 3

@io.on("connect")
def handle_connection():
    print("Connected to a client")


@io.on("message")
def handle_message(msg):
    print(msg)


@io.on("room")
def handle_room(room_id):
    print("Room started")
    # unpackage value from dict
    room_id = room_id["room_id"]
    # find the id in db
    room = db.rooms.find_one_or_404({"_id": ObjectId(oid=str(room_id))})
    # if we found the room
    if room != None:
        clients[room_id] = True
        # list of places so we dont have to keep looking them up
        places = []
        for place_id in room["places"]:
                place = db.places.find_one({ "_id": ObjectId(oid=str(place_id)) })
                # if the place has a numerical output
                places.append(place)
               
        # iterate through places and scrape data
        while clients[room_id] == True:
            for place in places:
                if place['output'] == 'int':
                    # try:
                    # data
                    data = scrapper.ScrapeXpath(place["url"], place["path"], interval)
                    # regex cleaning
                    cleaned_val =  float(('').join(re.findall('[\d/.]', data)))  # [int(s) for s in data.split() if s.isdigit()]
                    # timestamp
                    t = int(time.time())
                    print(t, data)
                    # emit to client
                    emit("point",{ "name": place["name"], "x": t, "y": cleaned_val })
                    # sleep to not overload socket
                    io.sleep(0.2)
                    # except:
                    #     t = int(time.time())
                    #     emit("point",{ "name": place["name"], "x": t, "y": 0 })


@io.on('stop')
def bye(msg):
    print("Closed room " + msg["room_id"])
    # stop room's run loop
    clients[msg["room_id"]] = False


@io.on_error()
def handle_error(e):
    print(e)


# module
if __name__ == '__main__':
    io.run(app, debug=True, host='0.0.0.0', port=port)


