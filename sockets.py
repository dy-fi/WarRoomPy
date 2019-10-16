from flask import Flask, render_template
from flask_socketio import socketio


socket_app = Flask("Socket_Room")