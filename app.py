from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_pymongo import PyMongo
import scrapper

app = Flask(__name__)
app.config.from_pyfile("config.cfg")
app.config['MONGO_URI'] = "mongodb://localhost:27017/wrdb"
db = PyMongo(app).db


@app.route("/", methods = ['GET'])
def index():
    return render_template("index.html")


@app.route("/room", methods = ['POST', 'GET'])
def make_room():
    if request.method == 'POST':
        title = request.form['title']
        name = request.form['name']
        url = request.form['url']
        path = request.form['path']

        Place = {
            'name': name,
            'url': url,
            'path': path,
            'values': []
        }

        place_id = db.rooms.insert_one(Place).inserted_id
        newRoomList = [place_id]

        Room = {
            'title': title,
            'places': newRoomList,
        }

        room_id = db.rooms.insert_one(Room).inserted_id
        return redirect(url_for("show_room", room_id=room_id))

    if request.method == 'GET':
        return render_template('room-form.html')


@app.route("/rooms", methods = ['GET'])
def show_rooms():
    rooms = db.rooms.find({})
    return render_template('rooms.html', rooms=rooms)


@app.route("/show_room")
def show_room(room_id):
    room = db.rooms.find_one_or_404(room_id)
    result = []

    for place_id in room['places']:
        place = db.rooms.find_one({ "_id": place_id })
        data = scrapper.ScrapeXpath(place['url'], place['path'])
        d = { 
            'name': place['name'],
            'data': data
        }
        result.append(d)
    
    return render_template("room.html", room=room, data=result)
    
