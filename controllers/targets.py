from flask import Blueprint, render_template, redirect, url_for, request
from database import mongo
from bson import ObjectId
import re
import time
import scrapper

db = mongo.db

target_bp = Blueprint('target', __name__,template_folder='templates')
interval = 3

@target_bp.route("/target/form", methods = ["POST", "GET"])

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
        output = request.form["output"]

        # Place struct
        Place = {
            "name": name,
            "url": url,
            "path": path,
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
        return redirect(url_for("target.target", room_id=room_id))


@target_bp.route("/targets")
def show_rooms():
    """
    show all rooms
    test route, remove in PROD
    """
    rooms = db.rooms.find({})
    return render_template("rooms.html", rooms=rooms)


@target_bp.route("/target/<room_id>", methods = ["GET"])
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
        data = scrapper.ScrapeXpath(place["url"], place["path"], interval)
        # if we find data
        if data != None:
            print(data, "----")
            
            # if the output type is 'int', we'll want to just extract the numerical value from the data
            if place['output'] == 'int':    
                data = float(('').join(re.findall('[\d/.]', data)))

            print(data)
            # time for values
            t = int(time.time())

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
                    {"values": -1}
                })

        # response packaging
        d = { 
            "name": place["name"],
            "values": place["values"]
        }

        result.append(d)
    
    return render_template("room.html", room=room, data=result)
