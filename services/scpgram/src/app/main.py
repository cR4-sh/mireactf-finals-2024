from app.routes import common_blueprint
from app.api import api_blueprint
import secrets
from app.utils import socketio, app

app.register_blueprint(common_blueprint)
app.register_blueprint(api_blueprint)
app.secret_key = secrets.token_hex(16)

socketio.init_app(app)

