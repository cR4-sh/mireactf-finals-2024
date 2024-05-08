#!/usr/bin/env -S python3
import sys

from checklib import *
from checklib import status
from faker import Faker
import random
import string

import acms_api


fake_flag = lambda: ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))


class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 20
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.acms = acms_api.ACMS(self.host)

    def check(self):
        username = rnd_username(10)
        password = rnd_password()

        if not self.acms.connect():
            self.cquit(Status.DOWN)

        if not self.acms.create_user(username, password):
            self.cquit(Status.MUMBLE)
        
        if not self.acms.login(username, password):
            self.cquit(Status.MUMBLE)

        logs = self.acms.get_logs()
        if len(logs) != 1 or not logs[0].endswith(f'Successfully logged in as {username}!'):
            self.cquit(Status.MUMBLE)

        msg = Faker().text(120)
        if not self.acms.add_log(msg):
            self.cquit(Status.MUMBLE)

        logs = self.acms.get_logs()
        if len(logs) != 2 or not logs[1].endswith(msg):
            self.cquit(Status.MUMBLE)

        if not self.acms.delete_log(random.randint(1, 2)):
            self.cquit(Status.MUMBLE)
            
        if not self.acms.get_logs():
            self.cquit(Status.MUMBLE)

        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        username = rnd_username(10)
        password = rnd_password()

        if not self.acms.connect():
            self.cquit(Status.DOWN)

        if not self.acms.create_user(username, password):
            self.cquit(Status.MUMBLE)

        if not self.acms.login(username, password):
            self.cquit(Status.MUMBLE)
        
        uuid = self.acms.get_profile()
        if not uuid:
            self.cquit(Status.MUMBLE)

        self.acms.create_group(Faker().text(32))

        plebeians = []

        for _ in range(random.randint(1, 5)):
            un, p, a = rnd_username(10), rnd_password(), min(int(1/(3*random.random())+0.7), 5)
            if a < 5:
                plebeians.append((un, p, a))
            
            if not self.acms.create_user(un, p):
                self.cquit(Status.MUMBLE)

            if not self.acms.add_user_to_group(un, a):
                self.cquit(Status.MUMBLE)

        device = self.acms.add_device_to_group(5, 1, flag)
        if not device:
            self.cquit(Status.MUMBLE)

        for _ in range(random.randint(1, 5)):
            ac, a = fake_flag(), min(int(1/(3*random.random())+0.7), 5)
            
            if not self.acms.add_device_to_group(a, random.randint(2, 5), ac):
                self.cquit(Status.MUMBLE)

        plebeian = ('', '', 0)
        if plebeians:
            plebeian = random.choice(plebeians)

        self.cquit(Status.OK, uuid, f'{username}:{password}:{plebeian[0]}:{plebeian[1]}:{str(plebeian[2])}:{device}')

    def get(self, flag_id: str, flag: str, vuln: str):
        head_un, head_p, plebeian_un, plebeian_p, plebeian_a, device = flag_id.split(':')

        if not self.acms.connect():
            self.cquit(Status.DOWN)

        if not self.acms.login(head_un, head_p):
            self.cquit(Status.MUMBLE)

        members, devices = self.acms.show_group()
        if not members or not devices:
            self.cquit(Status.MUMBLE)

        if devices[0] != [device, 'Access controller', '5']:
            self.cquit(Status.MUMBLE)

        if self.acms.get_device(devices[0][0]) != flag:
            self.cquit(Status.CORRUPT)

        if not self.acms.get_device(random.choice(devices[1:])[0]):
            self.cquit(Status.MUMBLE)

        if not self.acms.logout():
            self.cquit(Status.MUMBLE)

        if plebeian_un:
            if not self.acms.login(plebeian_un, plebeian_p):
                self.cquit(Status.MUMBLE)

            if not self.acms.get_profile():
                self.cquit(Status.MUMBLE)

            if self.acms.get_device(devices[0][0]):
                return self.cquit(Status.MUMBLE)

            devices = list(filter(lambda d: int(d[2]) <= int(plebeian_a), devices))

            if devices:
                if not self.acms.get_device(random.choice(devices)[0]):
                    self.cquit(Status.MUMBLE)

        self.cquit(Status.OK)
        

if __name__ == '__main__':
    c = Checker(sys.argv[2])
    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception() as e:
        cquit(status.Status(c.status), c.public, c.private)