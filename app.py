from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import ObjectId
from flask_socketio import SocketIO, send, emit
import scrapper
import time
import datetime
import json


# ==============Server Init================
app = Flask(__name__)

# enable CORS where its needed
cors = CORS(app, resources={r"/target/ws"})
# config
app.config.from_pyfile("config.cfg")
app.config["SECRET_KEY"] = 'not the real secret lol'
app.config["MONGO_URI"] = "mongodb://localhost:27017/wrdb"
mongo = PyMongo(app)
db = mongo.db

# ================Sockets==================

io = SocketIO(app)


# ================Routes===================


# ================Index====================

@app.route("/", methods = ["GET"])
def index():
    return render_template("index.html")


# ================Rooms====================

@app.route("/room", methods = ["POST", "GET"])
def make_room():
    """
    Create a new room or render room form depending on method
    """

    # gets the room form
    if request.method == "GET":
        return render_template("room-form.html")

    # post request makes a new room
    if request.method == "POST":
        # load form data
        title = request.form["title"]
        name = request.form["name"]
        url = request.form["url"]
        path = request.form["path"]
        interval = request.form["interval"]
        output = request.form["output"]

        # Place struct
        Place = {
            "name": name,
            "url": url,
            "path": path,
            "interval": interval,
            "output": output,
            "values": []
        }

        place_id = db.places.insert_one(Place).inserted_id
        newRoomList = [place_id]
        # Room struct
        Room = {
            "title": title,
            "places": newRoomList,
        }
        # insert and view the new room
        room_id = db.rooms.insert_one(Room).inserted_id
        return redirect(url_for("target", room_id=room_id))


@app.route("/rooms", methods = ["GET"])
def show_rooms():
    """
    show all rooms
    test route, remove in PROD
    """
    rooms = db.rooms.find({})
    return render_template("rooms.html", rooms=rooms)


@app.route("/room/<room_id>", methods = ["GET"])
def target(room_id):
    """
    display room
    """
    # find room or bust!
    room = db.rooms.find_one({ "_id" : ObjectId(oid=str(room_id)) })
    print(room)
    # list of dictionaries after its populated in the proceeding for loop
    result = []
    # iterate through places and scrape data
    for place_id in room["places"]:
        print(place_id)
        place = db.places.find_one({ "_id": ObjectId(oid=str(place_id)) })
        data = scrapper.ScrapeXpath(place["url"], place["path"], place["interval"])
        # if we find data
        if data != None:
            print(data)
            
            # if the output type is 'int', we'll want to just extract the numerical value from the data
            if place['output'] == 'int':    
                data = [int(s) for s in data.split() if s.isdigit()]

            # time for values
            t = int(time.mktime(datetime.datetime.now().timetuple()))


            # push new val to mongo document
            db.places.update_one(
            {"_id": ObjectId(oid=str(place_id))},
            {
                "$push":
                {"values": {"time": t, "data": data}}
            })

            # pop to keep the value lists at 10
            if len(place["values"]) > 9:
                db.places.update_one(
                {"_id": ObjectId(oid=str(place_id))},
                {
                    "$pop":
                    {"values": 1}
                })

        # response packaging
        d = { 
            "name": place["name"],
            "values": place["values"]
        }

        result.append(d)
    
    return render_template("room.html", room=room, data=result)


# ================Sockets==================

@app.route("/target/ws/<room_id>")
def target_ws(room_id):
    room = db.rooms.find_one_or_404(ObjectId(oid=str(room_id)))
    places = []
    for place_id in room["places"]:
        place = db.places.find_one({"_id": ObjectId(oid=str(place_id))})
        places.append(place)
    print(places)
    return render_template("live-room.html", room=room, places=places)

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
    room = db.rooms.find_one({"_id": ObjectId(oid=str(room_id))})
    # if we found the room
    if room != None:
        
        # list of places so we dont have to keep looking them up
        places = []
        for place_id in room["places"]:
                place = db.places.find_one({ "_id": ObjectId(oid=str(place_id)) })
                # if the place has a numerical output
                places.append(place)
               
        # iterate through places and scrape data
        while True:
            for place in places:
                data = scrapper.ScrapeXpath(place["url"], place["path"], place["interval"])
                data = [int(s) for s in data.split() if s.isdigit()]
                t = int(time.mktime(datetime.datetime.now().timetuple()))
                print(t, data)
                emit("point",{ "name": str(place["name"]), "time": t, "y": data })
                io.sleep(0)


@io.on_error()
def handle_error(e):
    print(e)

@io.on('disconnect')
def bye():
    print("client disconnected")


# ================Places===================

@app.route("/place", methods = ["POST"])
def make_place():
    """
        create a new place from form data, add it to db, redirect to relevent room
    """
    print(request.form['room_id'])
    room_id = ObjectId(oid=str(request.form['room_id']))
    live = True
    # place struct packaging
    if int(request.form["interval"]) > 200:
        live = False

    newPlace = {
        "name": request.form["name"],
        "url": request.form["url"],
        "path": request.form["path"],
        "interval": request.form["interval"],
        "output": request.form["output"],
        "live": live,
        "values": [],
    }

    newPlace_id = db.places.insert_one(newPlace).inserted_id
    # push to room's places list
    db.rooms.find_one_and_update(
    {"_id": room_id },
    {
        "$push":
        {"places": newPlace_id}
    })
    # redirect to room
    return redirect(url_for("target", room_id=room_id))

if __name__ == '__main__':
    io.run(app, debug=True, host='localhost', port=5000)