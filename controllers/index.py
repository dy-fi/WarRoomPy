from flask import Blueprint, render_template, abort
from flask_jwt_extended import get_jwt_identity, jwt_optional
from database import mongo

db = mongo.db

index_bp = Blueprint('index', __name__, template_folder='templates')

@index_bp.route("/", methods = ["GET"])
@jwt_optional
def index():
    current_user = get_jwt_identity
    if current_user:
        return render_template("index.html", user=current_user)
    else:
        return render_template("index.html")


@index_bp.route("/how-to", methods = ["GET"])
def howto():
    return render_template("how-to.html")

@index_bp.errorhandler(404)
def fourohfour(error):
    msg = "Target Lost"
    return render_template("error.html", msg=msg, err=error)
