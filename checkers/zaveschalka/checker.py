#!/usr/bin/env -S python3
import random
import sys

from checklib import *
from checklib import status
import logging

import will_lib

ALPH = [chr(i) for i in range(65, 65 + 26)] + [chr(i) for i in range(97, 97 + 26)]

class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 15
    uses_attack_data: bool = True

    req_ua_agents = ['python-requests/2.{}.0'.format(x) for x in range(15, 28)]
    req_ua_agents += ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.{}'.format(x) for x in range(30, 40)]
    req_ua_agents += ['MEREACTF', 'HELLO_FROM_MIREA', 'BEBEBEBBEBE', 'BEBRA', 'ROBERT SAMA']

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.lib = will_lib.WillLib(self)
    
    @property
    def _random_length(self) -> int:
        return random.randint(3,15)
    
    @property
    def _random_phone(self) -> int:
        return str(random.randint(1000000, 10000000))
    
    @property
    def _random_chars(self) -> str:    
        return rnd_string(self._random_length, ALPH)

    def _session_with_req_ua(self):
        sess = get_initialized_session()
        if random.randint(0, 10) != 1:
            sess.headers['User-Agent'] = random.choice(self.req_ua_agents)
            
        #sess.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        return sess

    def check(self):
        session1 = self._session_with_req_ua()
        session2 = self._session_with_req_ua()

        username1, password1, email1, phone1 = rnd_username(), rnd_password(), f'{self._random_chars}@{self._random_chars}.{self._random_chars}', self._random_phone
        username2, password2, email2, phone2 = rnd_username(), rnd_password(), f'{self._random_chars}@{self._random_chars}.{self._random_chars}', self._random_phone
        
        # Проверяем регистрацию
        self.lib.register(session1, username1, password1, email1, phone1)
        self.lib.register(session2, username2, password2, email2, phone2)

        # Проверяем логин с чистой сессией
        clear_session = self._session_with_req_ua()
        self.lib.login(clear_session, username1, password1, email1, phone1)
    
        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        # Регистрируем первого пользователя
        session1 = self._session_with_req_ua()
        username1, password1, email1, phone1 = rnd_username(), rnd_password(), f'{self._random_chars}@{self._random_chars}.{self._random_chars}', self._random_phone
        self.lib.register(session1, username1, password1, email1, phone1)

        # Регистрируем второго пользователя
        session2 = self._session_with_req_ua()
        username2, password2, email2, phone2 = rnd_username(), rnd_password(), f'{self._random_chars}@{self._random_chars}.{self._random_chars}', self._random_phone
        self.lib.register(session2, username2, password2, email2, phone2)

        # Создаем заметку от первого пользователя и шарим второму
        title = self._random_chars
        will_id = self.lib.create_will(session1, title, flag, username2)

        self.cquit(Status.OK, '{"username1": "' + username1 + '", "username2": "' + username2 + '", "will_id": "'+ will_id+'"}', f"{username1}:{password1}:{username2}:{password2}:{will_id}")

    def get(self, flag_id: str, flag: str, vuln: str):
        username1, password1, username2, password2, will_id = flag_id.split(':')
        
        # Логинимся за первого пользователя
        session1 = self._session_with_req_ua()
        self.lib.login(session1, username1, password1, status=Status.CORRUPT)

        # Проверяем доступ к флагу
        self.lib.check_will(session1, will_id, flag)
        
        # Логинимся за второго пользователя
        session2 = self._session_with_req_ua()
        self.lib.login(session2, username2, password2, status=Status.CORRUPT)

        # Проверяем доступ к флагу от пользователя, которому шарили записку
        self.lib.check_will(session2, will_id, flag, True)

        self.cquit(Status.OK)


if __name__ == '__main__':
    c = Checker(sys.argv[2])
    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception() as e:
        cquit(status.Status(c.status), c.public, c.private)
