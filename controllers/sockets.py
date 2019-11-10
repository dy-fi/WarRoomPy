from flask import Blueprint, render_template
from database import mongo
from bson import ObjectId

db = mongo.db

socket_bp = Blueprint('sockets', __name__, template_folder='templates')

@socket_bp.route("/target/ws/<room_id>")
def targetWS(room_id):
    room = db.rooms.find_one_or_404(ObjectId(oid=str(room_id)))
    places = []
    for place_id in room["places"]:
        place = db.places.find_one({"_id": ObjectId(oid=str(place_id))})
        places.append(place)
    return render_template("live-room-2.html", room=room, places=places)

