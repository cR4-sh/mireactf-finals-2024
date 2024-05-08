from pwn import *


PORT = 1079


class ACMS(object):
    def __init__(self, host: str) -> None:
        self.host = host
        
    def connect(self) -> bool:
        try:
            self.r = remote(self.host, PORT, timeout=3)
            self.r.timeout = 0.5
        except pwnlib.exception.PwnlibException:
            return False

        self.r.rl = self.r.recvline
        self.r.ru = self.r.recvuntil
        self.r.sl = self.r.sendline

        return True

    def create_user(self, username: str, password: str) -> bool:
        try:
            self.r.ru(b'\n[>]')
            self.r.sl(b'1')
            self.r.rl()
            self.r.sl(username.encode())
            self.r.rl()
            self.r.sl(password.encode())
            return self.r.ru(f'User {username} created successfully'.encode())

        except (pwnlib.exception.PwnlibException, EOFError):
            return False

    def login(self, username: str, password: str) -> bool:
        try:
            self.r.ru(b'\n[>]')
            self.r.sl(b'2')
            self.r.rl()
            self.r.sl(username.encode())
            self.r.rl()
            self.r.sl(password.encode())
            return self.r.ru(f'Successfully logged in as {username}'.encode())

        except (pwnlib.exception.PwnlibException, EOFError):
            return False
        
    def logout(self) -> bool:
        try:
            self.r.ru(b'\n[>]')
            self.r.sl(b'4')
            return self.r.ru(b'Logged out!')

        except (pwnlib.exception.PwnlibException, EOFError):
            return False

    def get_profile(self) -> str:
        try:
            self.r.ru(b'\n[>]')
            self.r.sl(b'3')
            self.r.ru(b'USER UUID     : ')
            ret = self.r.rl().decode().strip()
            self.r.sl()
            return ret
         
        except (pwnlib.exception.PwnlibException, EOFError): # TODO тута еще могут быть эксэпшены!!!
            return ''
        
    def create_group(self, groupname: str) -> bool:
        try:
            self.r.ru(b'\n[>]')
            self.r.sl(b'5')
            self.r.rl()
            self.r.sl(groupname.encode())
            return self.r.ru(f'Group {groupname} created successfully'.encode())
         
        except (pwnlib.exception.PwnlibException, EOFError):
            return False
        
    def add_user_to_group(self, username: str, access: int) -> bool:
        try:
            self.r.ru(b'\n[>]')
            self.r.sl(b'6')
            self.r.rl()
            self.r.sl(username.encode())
            self.r.rl()
            self.r.sl(str(access).encode())
            return self.r.ru(f'User {username} added to group successfully'.encode())
         
        except (pwnlib.exception.PwnlibException, EOFError):
            return False
    
    def show_group(self) -> bool:
        try:
            self.r.ru(b'[>]')
            self.r.sl(b'7')
            self.r.ru(b'+----------------------------------+--------\n')
            members = [list(map(str.strip, u.split(' | ')))[1:] for u in self.r.ru(b'\n\n').decode().split('\n') if u]
            self.r.ru(b'+----------------------------------+--------\n')
            devices = [list(map(str.strip, d.split(' | ')))[1:] for d in self.r.ru(b'\n\n').decode().split('\n') if d]
            self.r.sl()
            return members, devices
         
        except (pwnlib.exception.PwnlibException, EOFError):
            return [], []

    def add_device_to_group(self, access: int, device: int, access_key: str) -> bool:
        try:
            self.r.ru(b'\n[>]')
            self.r.sl(b'8')
            self.r.ru(b'\n[>]')
            self.r.sl(str(device).encode())
            self.r.rl()
            self.r.sl(str(access).encode())
            self.r.rl()
            self.r.sl(access_key.encode())
            self.r.ru(b'[*] Last command log: Device ')
            return self.r.rl().decode().strip().split()[0]
              
        except (pwnlib.exception.PwnlibException, EOFError):
            return ''
    
    def get_device(self, device_id: str) -> str:
        try:
            self.r.ru(b'\n[>]')
            self.r.sl(b'9')
            self.r.rl()
            self.r.sl(device_id.encode())
            
            if not self.r.ru(b'ACCESS KEY    : '):
                return ''
            
            ret = self.r.rl().decode().strip()
            self.r.sl()
            return ret
              
        except (pwnlib.exception.PwnlibException, EOFError):
            return ''
        
    def get_logs(self) -> list[str]:
        try:
            self.r.ru(b'\n[>]')
            self.r.sl(b'13')
            if not self.r.ru(b'log journal:\n\n'):
                return ['']

            logs = []
            l = self.r.recvline()
            while l and len(logs) < 16:
                logs.append(l.decode().strip())
                l = self.r.recvline()

            self.r.sl()
            return logs
              
        except (pwnlib.exception.PwnlibException, EOFError):
            return []
    
    def add_log(self, msg: str) -> bool:
        try:
            self.r.ru(b'\n[>]')
            self.r.sl(b'11')
            self.r.rl()
            self.r.sl(msg.encode())
            return self.r.ru(f'Last command log: {msg}'.encode())
              
        except (pwnlib.exception.PwnlibException, EOFError):
            return False

    def delete_log(self, ind: int) -> bool:
        try:
            self.r.ru(b'\n[>]')
            self.r.sl(b'12')
            self.r.rl()
            self.r.sl(str(ind).encode())
            return self.r.ru(b'Successfully completed')
              
        except (pwnlib.exception.PwnlibException, EOFError):
            return False