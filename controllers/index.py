from flask import Blueprint, render_template, abort, redirect, url_for
from database import mongo
from auth import auth

db = mongo.db

index_bp = Blueprint('index', __name__, template_folder='templates')

@index_bp.route("/", methods = ["GET"])
def index():
    return render_template("index.html")
    
@index_bp.route("/how-to", methods = ["GET"])
def howto():
    return render_template("how-to.html")

@index_bp.errorhandler(404)
def fourohfour(error):
    msg = "Target Lost"
    return render_template("error.html", msg=msg, err=error)
