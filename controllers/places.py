from flask import Blueprint, render_template, redirect, url_for, request
from database import mongo
from bson import ObjectId

db = mongo.db

place_bp = Blueprint('places', __name__, template_folder='templates')

@place_bp.route('/place')
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
