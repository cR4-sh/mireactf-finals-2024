from flask import Blueprint, render_template, request, session, redirect, send_from_directory, \
    url_for
from functools import wraps
import app.db as db
from app.utils import app 


common_blueprint = Blueprint('common', __name__, template_folder='app/templates')


def middlevare():
    def check_session(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'username' not in session:
                return redirect('/login', code=302)
            return f(*args, **kwargs)
        return wrapper
    return check_session


@common_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect('/')
    if request.method == 'POST':
        action = request.form['action']
        username = request.form['username']
        password = request.form['password']

        if action == 'signin':
            res = db.signin(str(username), password)
            if  'Successfully' in res:
                session['username'] = username
                return redirect('/')            
            return render_template('auth.html', error=res), 403
        if action == 'signup':
            res = db.signup(username,password)
            if 'Successfully' in res:
                return render_template('auth.html', error=res)
            return render_template('auth.html', error=res), 403

        return render_template('auth.html', error='incorrect action')

    return render_template('auth.html')


@common_blueprint.route('/logout', methods=['GET'])
@middlevare()
def logout():
    session.pop('username', None)
    return redirect('/login')

@common_blueprint.route('/', methods=['GET'])
@middlevare()
def profile():
    return render_template('main.html', methods=['GET'])


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')


@app.route('/chat/<uuid:chat_uuid>')
@middlevare()
def chat_room(chat_uuid):
    res = db.check_access(session['username'], chat_uuid)
    if res:
        return res, 403
    chat_name = db.get_chatName(chat_uuid)
    return render_template('chat.html', chat_id=chat_uuid, chat_name=chat_name)
