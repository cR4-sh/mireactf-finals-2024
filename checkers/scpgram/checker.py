#!/usr/bin/env -S python3
import random
import sys

from checklib import *
from checklib import status

import scpgram_lib


class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 15
    uses_attack_data: bool = True

    req_ua_agents = ['python-requests/2.{}.0'.format(x) for x in range(15, 28)]

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.lib = scpgram_lib.TestLib(self)

    def session_with_req_ua(self):
        sess = get_initialized_session()
        if random.randint(0, 1) == 1:
            sess.headers['User-Agent'] = random.choice(self.req_ua_agents)
        return sess

    def random_route_name(self):
        return 'Expedition #{}'.format(random.randint(1, 10000))

    def check(self):
        session = self.session_with_req_ua()
        session1 = self.session_with_req_ua()
        username, password = rnd_username(), rnd_password()
        username1, password1 = rnd_username(), rnd_password()

        ping = self.lib.ping()
        if not ping:
            self.cquit(Status.DOWN)

        self.lib.signup(session1, username1, password1)

        self.lib.signup(session, username, password)
        self.lib.signin(session, username, password)
        chat_uuid = self.lib.createChat(session)

        invite = self.lib.addUserToChat(session, chat_uuid,username1)
        if invite != 1:
            self.cquit(Status.MUMBLE)

        check_invite = self.lib.getChatUsers(session, chat_uuid,username1)
        if check_invite != 1:
            self.cquit(Status.MUMBLE)

        remove = self.lib.removeUserFromChat(session, chat_uuid,username1)
        if remove != 1:
            self.cquit(Status.MUMBLE)        
        
        check_remove = self.lib.getChatUsers(session, chat_uuid,username1)
        if check_remove != 0:
            self.cquit(Status.MUMBLE)

        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        sess = self.session_with_req_ua()
        u = rnd_username()
        p = rnd_password()

        self.lib.signup(sess, u, p)
        self.lib.signin(sess, u, p)
        chat_uuid = self.lib.createChat(sess)

        send_mess = self.lib.sendMessage(sess.cookies.get_dict()['session'], chat_uuid, flag, u)

        if send_mess == 1:
            self.cquit(Status.OK, chat_uuid, f"{u}:{p}:{chat_uuid}")

        self.cquit(Status.MUMBLE)

    def get(self, flag_id: str, flag: str, vuln: str):
        u, p, chat_uuid = flag_id.split(':')
        sess = self.session_with_req_ua()
        self.lib.signin(sess, u, p, status=Status.CORRUPT)

        check = self.lib.getMessage(sess.cookies.get_dict()['session'], chat_uuid, flag, u)
        if check == 0:
            self.cquit(Status.CORRUPT)
        
        self.cquit(Status.OK)

if __name__ == '__main__':
    c = Checker(sys.argv[2])
    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception() as e:
        cquit(status.Status(c.status), c.public, c.private)