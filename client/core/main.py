import hashlib
from core import client_socket
from core.features import Features
from conf import settings


class Main:
    def __init__(self):
        self.client = client_socket.ClientSocket((settings.HOST, settings.PORT))
        self.server_address = self.client.server_address
        self.socket = self.client.socket
        self.is_login = False  # 登录状态
        self.cmds = None

    def run(self):
        # a = sys.argv
        while True:
            if self.is_login is False:
                username = input('username:').strip()
                password = input('password:').strip()
                password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
                self.client.header(self.socket, (username, password_hash))
                self.is_login = self.client.unheader(self.socket)
                if not self.is_login:
                    print('username or password is bad.')
                    continue
                self.client.username = username  # 当登录成功后把username与客户端关联起来

                user_quotation = self.client.unheader(self.socket)  # 登录成功后接收用户已使用与可使用的储存空间
                used_quotation = user_quotation[0] / 1024 / 1024
                total_quotation = user_quotation[1]
                self.client.usable_quotation = total_quotation - used_quotation
                quotation = '''
                \rUsed Size  :      <%f>MB
                \rUsable Size:      <%f>MB
                \rTotal Size :      <%f>MB
                ''' % (used_quotation, self.client.usable_quotation, total_quotation)  # 把存储信息打印出来
                print(quotation)

            cmd = input('>>: ').strip()
            if not cmd: continue

            self.cmds = cmd.split()
            func = Features(self.client, self.cmds)
            func.find()
            # func_name = '_%s' % self.cmds[0]
            # if hasattr(self, func_name):
            #     func = getattr(self, func_name)
            #     func()
