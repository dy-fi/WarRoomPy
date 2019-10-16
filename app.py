from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson import ObjectId
import scrapper

app = Flask(__name__)
app.config.from_pyfile("config.cfg")
app.config['MONGO_URI'] = "mongodb://localhost:27017/wrdb"
mongo = PyMongo(app)
db = mongo.db

@app.route("/", methods = ['GET'])
def index():
    return render_template("index.html")


@app.route("/room", methods = ['POST', 'GET'])
def make_room():

    # gets the room form
    if request.method == 'GET':
        return render_template('room-form.html')

    # post request makes a new room
    if request.method == 'POST':
        # load form data
        title = request.form['title']
        name = request.form['name']
        url = request.form['url']
        path = request.form['path']
        # Place struct
        Place = {
            'name': name,
            'url': url,
            'path': path,
            'values': []
        }

        place_id = db.places.insert_one(Place).inserted_id
        newRoomList = [place_id]
        # Room struct
        Room = {
            'title': title,
            'places': newRoomList,
        }
        # insert and view the new room
        room_id = db.rooms.insert_one(Room).inserted_id
        return redirect(url_for("show_room", room_id=room_id))


@app.route("/rooms", methods = ['GET'])
def show_rooms():
    rooms = db.rooms.find({})
    return render_template('rooms.html', rooms=rooms)


@app.route("/show_room/<room_id>", methods = ['GET'])
def show_room(room_id):
    # find room or bust!
    room = db.rooms.find_one({ "_id" : ObjectId(oid=str(room_id)) })
    print(room)
    # list of dictionaries after its populated in the proceeding for loop
    result = []
    # iterate through places and scrape data
    for place_id in room['places']:
        place = db.places.find_one({ "_id": ObjectId(oid=str(place_id)) })
        data = scrapper.ScrapeXpath(place['url'], place['path'])
        print(data)
        # response packaging
        d = { 
            'name': place['name'],
            'data': data,
            'values': place['values']
        }

        result.append(d)

        # push new val to mongo document
        db.places.update(
        {"_id": ObjectId(oid=str(place_id))},
        {
            "$push":
            {"values": data}
        })

        # pop to keep the value lists at 10
        if len(place['values']) > 9:
            db.places.update(
            {"_id": ObjectId(oid=str(place_id))},
            {
                "$pop":
                {"values": 1}
            })
        
    
    return render_template("room.html", room=room, data=result)
    
