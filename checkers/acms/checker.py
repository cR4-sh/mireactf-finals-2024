#!/usr/bin/env -S python3
import sys

from checklib import *
from checklib import status
from faker import Faker
import random
import string
import json

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
        un = rnd_username()
        p = rnd_password(random.randint(16, 30))

        self.assert_eq(self.acms.connect(), True, 'Failed to connect', Status.DOWN)
        self.assert_eq(self.acms.create_user(un, p), True, 'Failed to create user')
        self.assert_eq(self.acms.login(un, p), True, 'Failed to login')

        logs = self.acms.get_logs()
        if len(logs) != 1 or not logs[0].endswith(f'Successfully logged in as {un}!'):
            self.cquit(Status.MUMBLE)

        msg = Faker().text(120).replace('\n', ' ')

        self.assert_eq(self.acms.add_log(msg), True, 'Mumbled logs')

        logs = self.acms.get_logs()
        if len(logs) != 2 or not logs[1].endswith(msg):
            self.cquit(Status.MUMBLE)

        self.assert_eq(self.acms.delete_log(random.randint(1, 2)), True, 'Mumbled logs')
        self.assert_neq(self.acms.get_logs(), [], 'Mumbled logs')

        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        head_un = rnd_username()
        head_p = rnd_password(random.randint(16, 30))

        self.assert_eq(self.acms.connect(), True, 'Failed to connect', Status.DOWN)
        self.assert_eq(self.acms.create_user(head_un, head_p), True, 'Failed to create user')
        self.assert_eq(self.acms.login(head_un, head_p), True, 'Failed to login')
        
        uuid = self.acms.get_profile()

        self.assert_neq(uuid, '', 'Mumbled profile')
        self.assert_eq(self.acms.create_group(Faker().text(32).replace('\n', ' ')), True, 'Mumbled groups')

        plebeians = []

        for _ in range(random.randint(1, 5)):
            un, p, a = rnd_username(10), rnd_password(), min(int(1/(3*random.random())+0.7), 5)
            if 0 < a < 5:
                plebeians.append((un, p, a))

            self.assert_eq(self.acms.create_user(un, p), True, 'Failed to create user')
            self.assert_eq(self.acms.add_user_to_group(un, a), True, 'Mumbled groups')

        device = self.acms.add_device_to_group(5, 1, flag)
        self.assert_neq(device, '', 'Mumbled groups')

        for _ in range(random.randint(1, 5)):
            ac, a = fake_flag(), min(int(1/(3*random.random())+0.7), 5)
            self.assert_neq(self.acms.add_device_to_group(a, random.randint(2, 5), ac), '', 'Mumbled groups')

        plebeian = ('', '', 0)
        if plebeians:
            plebeian = random.choice(plebeians)

        self.cquit(Status.OK, json.dumps({'un':head_un, 'uuid':uuid}), f'{head_un}:{head_p}:{plebeian[0]}:{plebeian[1]}:{str(plebeian[2])}:{device}')

    def get(self, flag_id: str, flag: str, vuln: str):
        head_un, head_p, plebeian_un, plebeian_p, plebeian_a, device = flag_id.split(':')

        self.assert_eq(self.acms.connect(), True, 'Failed to connect', Status.DOWN)
        self.assert_eq(self.acms.login(head_un, head_p), True, 'Failed to login', Status.CORRUPT)

        members, devices = self.acms.show_group()
        if not members or not devices:
            self.cquit(Status.CORRUPT, 'Corrupted group')

        self.assert_eq(devices[0], [device, 'Access controller', '5'], 'Corrupted devices', Status.CORRUPT)
        self.assert_eq(self.acms.get_device(devices[0][0]), flag, 'Failed to retrive flag', Status.CORRUPT)
        self.assert_neq(self.acms.get_device(random.choice(devices[1:])[0]), '', 'Corrupted devices', Status.CORRUPT)
        self.assert_eq(self.acms.logout(), True, 'Mubled logout')

        if plebeian_un:
            self.assert_eq(self.acms.login(plebeian_un, plebeian_p), True, 'Failed to login', Status.CORRUPT)
            self.assert_neq(self.acms.get_profile(), '', 'Corrupted profile', Status.CORRUPT)
            self.assert_eq(self.acms.get_device(devices[0][0]), '', 'Corrupted devices', Status.CORRUPT)

            devices = list(filter(lambda d: int(d[2]) <= int(plebeian_a), devices))

            if devices:
                self.assert_neq(self.acms.get_device(random.choice(devices)[0]), '', 'Corrupted devices', Status.CORRUPT)

        self.cquit(Status.OK)
        

if __name__ == '__main__':
    c = Checker(sys.argv[2])
    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception() as e:
        cquit(status.Status(c.status), c.public, c.private)