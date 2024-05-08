import socketio
import random
import checklib
from checklib import BaseChecker
import requests
import os

PORT = 17788

sio = socketio.SimpleClient()

class TestLib:
    @property
    def api_url(self):
        return f'http://{self.host}:{self.port}'

    def __init__(self, checker: BaseChecker, port=PORT, host=None):
        self.c = checker
        self.port = port
        self.host = host or self.c.host

    def ping(self):
        try:
            requests.get(f'{self.api_url}')
            return 1
        except Exception as e:
            return 0

    def signup(self, session: requests.Session, username: str, password: str):
        resp = session.post(f'{self.api_url}/login', data={
            'username': username,
            'password': password,
            'action': 'signup'
        })
        self.c.assert_eq(resp.status_code, 200, 'Failed to signup')
        resp_data = self.c.get_text(resp, 'Failed to signup: invalid data')
        return resp_data

    def signin(self, session: requests.Session, username: str, password: str,
               status: checklib.Status = checklib.Status.MUMBLE):
        resp = session.post(f'{self.api_url}/login', data={
            'username': username,
            'password': password,
            'action': 'signin'
        })
        self.c.assert_eq(resp.status_code, 200, 'Failed to signin', status=status)
        resp_data = self.c.get_text(resp, 'Failed to signin: invalid data')
        return resp_data
    

    def createChat(self, session: requests.Session, status: checklib.Status = checklib.Status.MUMBLE):
        resp = session.post(f'{self.api_url}/api/chat/create', json={
            'chat_name': genChatName()
        })
        self.c.assert_eq(resp.status_code, 200, 'Cant create chat', status=status)
        chat_uuid = self.c.get_json(resp, 'Cant create chat: invalid data')['chat_id']

        return chat_uuid


    def addUserToChat(self, session: requests.Session, chat_uuid: str,  username: str, status: checklib.Status = checklib.Status.MUMBLE):
        resp = session.post(f'{self.api_url}/api/chat/{chat_uuid}/add_user', json={
            'username':username
        })
        self.c.assert_eq(resp.status_code, 200, 'Cant invite user', status=status)
        res = self.c.get_json(resp, 'Cant invite user: invalid data')['message']

        if 'successfully' in res:
            return 1
        return 0
    

    def getChatUsers(self, session: requests.Session, chat_uuid: str,  username: str, status: checklib.Status = checklib.Status.MUMBLE):
        resp = session.get(f'{self.api_url}/api/chat/{chat_uuid}/members')
        self.c.assert_eq(resp.status_code, 200, 'Cant get chat users', status=status)
        res = self.c.get_json(resp, 'Cant get chat users: invalid data')
        for user in res:
            if user['username'] == username:
                return 1
        return 0


    def removeUserFromChat(self, session: requests.Session, chat_uuid: str,  username: str, status: checklib.Status = checklib.Status.MUMBLE):
        resp = session.post(f'{self.api_url}/api/chat/{chat_uuid}/remove_user', json={
            'username':username
        })
        self.c.assert_eq(resp.status_code, 200, 'Cant remove user', status=status)
        res = self.c.get_json(resp, 'Cant remove user: invalid data')['message']

        if 'successfully' in res:
            return 1
        return 0
        

    def sendMessage(self, cookie: str, chat_uuid: str, flag: str, sender: str):
        try:
            sio.connect(f'{self.api_url}', headers={'Cookie':f'session={cookie}'})
            sio.emit('join_room', {'chat_id': chat_uuid})
            message = genMessage() + '`' + flag + '`'
            sio.emit('send_message', {'chat_id': chat_uuid, 'message':message})
            event = sio.receive()
            mess = event[1]['message']
            fin_flag = '<code>' + flag + '</code></p>'
            sio.disconnect()
            if fin_flag in mess and '<p>' in mess and sender == event[1]['sender']:
                return 1
            return 0
        except Exception:
            sio.disconnect()
            return 0
            
        
    def getMessage(self, cookie: str, chat_uuid: str, flag: str, sender: str):
        try:
            sio.connect(f'{self.api_url}', headers={'Cookie':f'session={cookie}'})
            sio.emit('join_room', {'chat_id': chat_uuid})
            sio.emit('get_messages', {'chat_id': chat_uuid})
            event = sio.receive()
            mess = event[1]['message']
            fin_flag = '<code>' + flag + '</code></p>'
            sio.disconnect()
            if fin_flag in mess and '<p>' in mess and sender == event[1]['sender']:
                return 1
            return 0
        except Exception:
            sio.disconnect()
            return 0



def genChatName():
    return 'SCP-' + str(random.randint(0,9999))

def genMessage():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, 'pasta.txt'), 'r', encoding='utf-8') as bank:
        lines = bank.readlines()
        random_line = random.choice(lines)
        return random_line
    