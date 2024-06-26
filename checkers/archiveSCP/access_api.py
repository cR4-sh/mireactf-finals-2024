from typing import Optional

import checklib
import random
import string
from checklib import BaseChecker
import requests
from bs4 import BeautifulSoup
import os

PORT = 2324
TIMEOUT = 5

script_dir = os.path.dirname(os.path.abspath(__file__))
images_path = os.path.join(script_dir, 'images')

image_files = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]


class AccessApi:
    @property
    def api_url(self):
        return f'http://{self.host}:{self.port}'


    def __init__(self, checker: BaseChecker, port=PORT, host=None):
        self.c = checker
        self.port = port
        self.host = host or self.c.host

    def GetScpName(self):
        return f"SCP-{''.join(random.choices(string.digits, k=3))}-{''.join(random.choices(string.digits, k=2))}{''.join(random.choices(string.ascii_lowercase, k=2))}"

    def ping(self):
        try:
            requests.get(f'{self.api_url}/', timeout=TIMEOUT)
            return 1
        except Exception as e:
            return 0
    def signup(self, session: requests.Session, username: str, password: str):
        resp = session.post(f'{self.api_url}/register', data={
            'username': username,
            'password': password,
        }, timeout=TIMEOUT)
        self.c.assert_nin("Такой пользователь уже существует!", resp.text, 'Failed to signup')
        resp_data = self.c.get_text(resp, 'Failed to signup: invalid data')
        return session

    def signin(self, session: requests.Session, username: str, password: str,
               status: checklib.Status = checklib.Status.MUMBLE):
        resp = session.post(f'{self.api_url}/login', data={
            'username': username,
            'password': password,
        }, timeout=TIMEOUT)
        self.c.assert_nin("Неправильное имя пользователя или пароль", resp.text, "Failed to login", status=status)
        return session
    
    def checkSCP(self, session: requests.Session, name: str, flag: str):
        # print(f'{self.api_url}/{name}')
        # print(session.cookies.get("department"))
        resp = session.get(f'{self.api_url}/{name}', cookies={"department": session.cookies.get("department")}, timeout=TIMEOUT)
        # print(resp.text)
        if flag in resp.text:
            return 1
        return 0
    
    def createDepartment(self, session: requests.Session, name: str):
        resp = session.post(f'{self.api_url}/create_department', data={"name_department":name}, timeout=TIMEOUT)
        self.c.assert_eq(resp.status_code, 200, 'Failed to create department')
        return name
    
    def createObject(self, session: requests.Session, name: str, description: str, flag: str):
        resp = session.post(f'{self.api_url}/create_scp', data={"name":name, "description":description + f"\n{flag}"}, files={"image": open(images_path+"/"+random.choice(image_files), 'rb')}, timeout=TIMEOUT)
        self.c.assert_eq(resp.status_code, 200, 'Failed to create SCP')
        return name
    
    def invite(self, session: requests.Session, name: str):
        resp = session.post(f"{self.api_url}/invite", data={"username": name}, timeout=TIMEOUT)
        self.c.assert_eq(resp.status_code, 200, 'Failed to invite')
    
    def checkStaff(self, session: requests.Session, name: str):
        resp = session.get(f"{self.api_url}/department", timeout=TIMEOUT)
        if name in resp.text:
            return 1
        return 0
    
    def checkList(self, session: requests.Session, name: str):
        resp = session.get(f"{self.api_url}/", cookies={"department": session.cookies.get("department")}, timeout=TIMEOUT)
        if name in resp.text:
            return 1
        return 0
    
    def checkInviteWhenInDepartment(self, session : requests.Session, name: str, department: str):
        resp = session.post(f"{self.api_url}/invite", data={"username": name}, timeout=TIMEOUT)
        if department in resp.text:
            return 1
        return 0





    
    
