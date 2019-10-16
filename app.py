from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson import ObjectId
import scrapper


# ==============Server Init================
app = Flask(__name__)
# config
app.config.from_pyfile("config.cfg")
app.config["MONGO_URI"] = "mongodb://localhost:27017/wrdb"
mongo = PyMongo(app)
db = mongo.db

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
        # Place struct
        Place = {
            "name": name,
            "url": url,
            "path": path,
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
        place = db.places.find_one({ "_id": ObjectId(oid=str(place_id)) })
        data = scrapper.ScrapeXpath(place["url"], place["path"])
        print(data)

        # push new val to mongo document
        db.places.update(
        {"_id": ObjectId(oid=str(place_id))},
        {
            "$push":
            {"values": data}
        })

        # pop to keep the value lists at 10
        if len(place["values"]) > 9:
            db.places.update(
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


# ================Places===================

@app.route("/room/<room_id>/place", methods = ["POST"])
def make_place(room_id):
    """
        create a new place from form data, add it to db, redirect to relevent room
    """
    
    room_id = ObjectId(oid=str(room_id))
    # place struct packaging
    newPlace = {
        "name": request.form["name"],
        "url": request.form["url"],
        "path": request.form["path"],
        "values": [],
    }
    # push to room's places list
    db.rooms.update(
    {"_id": room_id },
    {
        "$push":
        {"places": newPlace}
    })
    # redirect to room
    return redirect(url_for("target", room_id=room_id))

