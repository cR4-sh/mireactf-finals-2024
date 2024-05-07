from flask_socketio import SocketIO
from flask import Flask 


app = Flask(__name__, template_folder='templates', static_folder='static')

socketio = SocketIO(cors_allowed_origins = "*")
