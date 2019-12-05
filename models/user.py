from database import mongo
from flask_bcrypt import Bcrypt
from flask import current_app
from bson import ObjectId, json_util
from mongoengine import Document, DateTimeField, StringField, ReferenceField, ListField

from models.target import Target, Location

db = mongo.db 

bcrypt = Bcrypt(current_app)

class User(Document):

    username = StringField(max_length=60, required=True, unique=True)
    password = StringField(required=True)
    targets = ListField(ReferenceField(Target))
    banned = False
    admin = False
        
    def is_active(self):
        return db.users.find_one({"username"})["banned"] == False
    
    def get_id(self):
        try:
            json_util.dumps(db.users.find_one({"username" : self.username })["_id"])
        except:
            return None
