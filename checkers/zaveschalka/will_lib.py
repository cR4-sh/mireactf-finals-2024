from urllib.parse import urlparse, parse_qs
from checklib import BaseChecker, Status
import requests

PORT = 1782

class WillLib:
    @property
    def api_url(self):
        return f'http://{self.host}:{self.port}'

    def __init__(self, checker: BaseChecker, port=PORT, host=None):
        self.c = checker
        self.port = port
        self.host = host or self.c.host

    def _get_will_id(self, url: str) -> str:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        return query_params.get('id', [None])[0]

    def ping(self):
        try:
            requests.get(f'{self.api_url}')
            return 1
        except Exception as e:
            return 0
        
    def _check_profile(self, content: str, username: str, email: str, phone: str):
        self.c.assert_in(username, content, f'Failed to get profile data for {self.api_url} (username)')
        self.c.assert_in(email, content, f'Failed to get profile data for {self.api_url} (email)')
        self.c.assert_in(phone, content, f'Failed to get profile data for {self.api_url} (phone)')

    def register(self, session: requests.Session, username: str, password: str, email: str, phone: str):
        resp = session.post(f'{self.api_url}/register.php', data={
            'login': username,
            'password': password,
            'phone': phone,
            'email': email 
        })
        self.c.assert_in('profile.php', resp.url, f'Failed to register for {self.api_url}')
        self._check_profile(resp.text, username, email, phone)


    def login(self, session: requests.Session, username: str, password: str, email: str = "", phone: str = ""):
        resp = session.post(f'{self.api_url}/login.php', data={
            'login': username,
            'password': password
        })
        self.c.assert_in('profile.php', resp.url, f'Failed to login for {self.api_url}')
        self._check_profile(resp.text, username, email, phone)
    
    def create_will(self, session: requests.Session, title: str, will: str, username_to_share: str):
        resp = session.post(f'{self.api_url}/create_will.php', data={
            'title': title,
            'will': will,
            'username0': username_to_share
        })
        self.c.assert_nin('create_will.php', resp.url, 'Failed to create will')
        return self._get_will_id(resp.url)
    
    def check_will(self, session: requests.Session, will_id: str, flag: str, is_shared: bool = False):
        resp = session.get(f'{self.api_url}/will.php?id={will_id}')
        self.c.assert_in(flag, resp.text, f"Failed to get {'shared ' if is_shared else ''}will", Status.CORRUPT)