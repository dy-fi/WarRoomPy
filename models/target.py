from database import mongo
from bson import ObjectId, json_util
from mongoengine import Document, DateTimeField, StringField, ReferenceField, ListField, IntField

db = mongo.db 

class Location(Document):
    name = StringField(max_length=60, required=True)
    url = StringField(required=True)
    path = StringField(required=True)
    output = StringField(required=True)
    values = ListField(IntField())

class Target(Document):
    title = StringField(max_length=60, required=True)
    locations = ListField(ReferenceField(Location))

