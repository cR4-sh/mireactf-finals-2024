#!/usr/bin/env python3
import random
import re
import string
import sys

import requests
from faker import Faker
from checklib import *
from checklib import status

import access_api


class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 15
    uses_attack_data: bool = True

    req_ua_agents = ['python-requests/2.{}.0'.format(x) for x in range(15, 28)]

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.lib = access_api.AccessApi(self)
        self.id_regexp = re.compile(r'^[0-9A-Za-z]{1,40}$')

    def session_with_req_ua(self):
        sess = get_initialized_session()
        if random.randint(0, 1) == 1:
            sess.headers['User-Agent'] = random.choice(self.req_ua_agents)
        return sess

    def random_route_name(self):
        return 'Expedition #{}'.format(random.randint(1, 10000))

    def check(self):
        session = self.session_with_req_ua()
        username1, password1 = rnd_username(), rnd_password()
        username2, password2 = rnd_username(), rnd_password()
        department = rnd_username()
        scp = self.lib.GetScpName()

        ping = self.lib.ping()
        if not ping:
            self.cquit(Status.DOWN)

        self.lib.signup(session, username1, password1)
        self.lib.signup(session, username2, password2)
        session = self.lib.signin(session, username1, password1)
        self.lib.createDepartment(session, department)
        self.lib.createObject(session, scp, Faker('ru_RU').text(1000), "")
        self.lib.invite(session, username2)
        if not self.lib.checkStaff(session, username2):
            self.cquit(Status.MUMBLE)
       
        session = self.lib.signin(session, username2, password2)
        if not self.lib.checkList(session, scp):
            self.cquit(Status.MUMBLE)
        if not self.lib.checkSCP(session, scp, scp):
            self.cquit(Status.MUMBLE)


        self.cquit(Status.OK, )

    def put(self, flag_id: str, flag: str, vuln: str):
        ping = self.lib.ping()
        if not ping:
            self.cquit(Status.DOWN)
        sess = self.session_with_req_ua()
        u1 = rnd_username()
        p1 = rnd_password()
        u2 = rnd_username()
        p2 = rnd_password()
        department = rnd_username()

        self.lib.signup(sess, u1, p1)
        self.lib.signup(sess, u2, p2)
        session = self.lib.signin(sess, u1, p1)

        self.lib.createDepartment(sess, department)
        name_scp = self.lib.createObject(sess, self.lib.GetScpName(), Faker('ru_RU').text(1000), flag)
        self.lib.invite(session, u2)
        if name_scp:
            self.cquit(Status.OK, '{"username": "' + u1 + '","department":"' + department + '"}', f"{u2}:{p2}:{name_scp}")

        self.cquit(Status.MUMBLE)

    def get(self, flag_id: str, flag: str, vuln: str):
        ping = self.lib.ping()
        if not ping:
            self.cquit(Status.DOWN)
        u, p, name_scp = flag_id.split(':')
        sess = self.session_with_req_ua()
        sess = self.lib.signin(sess, u, p, status=Status.CORRUPT)

        check = self.lib.checkSCP(sess, name_scp, flag)
        if not check:
            self.cquit(Status.CORRUPT)

        self.cquit(Status.OK)

if __name__ == '__main__':
    c = Checker(sys.argv[2])
    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception() as e:
        cquit(status.Status(c.status), c.public, c.private)