from flask import Blueprint, jsonify, request, session
from app.utils import socketio
from flask_socketio import emit, join_room
import markdown2
import app.db as db
from datetime import datetime
from app.routes import middlevare
api_blueprint = Blueprint('api', __name__, url_prefix='/api')
timestamp = datetime.now()
timestamp_str = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')


@api_blueprint.route('/chat/create', methods=['POST'])
@middlevare()
def create_chat():
    data = request.json
    chat_name = data.get('chat_name')
    if chat_name == '':
        return jsonify({'error': 'must be named'})

    chat_id = db.create_chat(session['username'], chat_name)
    return jsonify({'chat_id': chat_id})


@api_blueprint.route('/chat/<uuid:chat_id>/members', methods=['GET'])
@middlevare()
def chat_members(chat_id):
    username = session['username']
    res = db.get_usersInChat(username, chat_id)
    if 'no access' in res:
        return jsonify({'error':'no access'}), 403
    users_list = [{'username':user[0]} for user in res]
    return jsonify(users_list)


@api_blueprint.route('/chat/<uuid:chat_id>/add_user', methods=['POST'])
@middlevare()
def add_user_to_chat(chat_id):
    data = request.json
    username = data.get('username')
    res = db.chat_add_user(session['username'],chat_id,username)
    return jsonify({'message': res})


@api_blueprint.route('/chat/<uuid:chat_id>/remove_user', methods=['POST'])
@middlevare()
def remove_user_from_chat(chat_id):
    data = request.json
    username = data.get('username')
    res = db.chat_remove_user(session['username'],chat_id,username)
    return jsonify({'message': res})


@api_blueprint.route('/users', methods=['GET'])
@middlevare()
def get_users():
    users = db.get_users()
    users_list = [{'username':user[0]} for user in users]
    return jsonify(users_list)


@api_blueprint.route('/chats', methods=['GET'])
@middlevare()
def get_chats():
    chats = db.get_userChats(session['username'])
    chats_list = [{'chat_name': chat[0], 'chat_id': chat[1]} for chat in chats]
    return jsonify(chats_list)


@socketio.on('join_room')
@middlevare()
def handle_connect(data):
    chat_id = data['chat_id']
    if chat_id:
        join_room(chat_id)


@socketio.on('send_message')
@middlevare()
def send_message(data):
    chat_uuid = data['chat_id']
    message = data['message']
    username = session['username']
    res = db.save_message(chat_uuid, message, username)
    message = markdown2.markdown(message)
    if res == 'OK':
        emit('message_received', {'message': message, 'timestamp':timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'), 'sender':username}, room=chat_uuid)


@socketio.on('get_messages')
@middlevare()
def get_messages(data):
    chat_uuid = data['chat_id']
    messages = db.get_messages(chat_uuid)
    for msg in messages:
        timestamp_str = msg[1].strftime('%Y-%m-%dT%H:%M:%SZ')
        emit('message_received', {'message': markdown2.markdown(msg[0]), 'timestamp': timestamp_str, 'sender': msg[2]})