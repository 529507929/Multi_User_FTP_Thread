import os
from conf.account import account
from conf import settings


class Cd:
    def __init__(self, cmds, server, conn, pwd, username):
        if len(cmds) > 1:
            self.new_dir = cmds[1]
        else:
            self.new_dir = None
        self.cmds = cmds
        self.old_dir = pwd
        self.server = server
        self.conn = conn
        self.result = False
        self.pwd = pwd
        self.username = username

    def run(self):
        if self.new_dir == '..':
            self.server.header(self.conn, self.pwd)
            old_dir_list = self.old_dir.split('\\')
            if old_dir_list[-1] != self.username:
                self.pwd = '\\'.join(old_dir_list[:-1])
                log = '%s enter %s' % (self.username, self.pwd)
                self.server.wri_log(settings.SERVER_ROOT_DIR, 'log\\server.log', log)
                print(log)
        elif self.new_dir:
            account_path = account[self.username]['home']
            comple_path = self.server.path_process(self.new_dir, self.pwd)
            if os.path.exists(comple_path) and account_path == comple_path[:len(account_path)]:  # 判断路径是否存在
                self.pwd = comple_path
                self.result = True
                # 记录日志
                log = '%s enter %s' % (self.username, comple_path)
                self.server.wri_log(settings.SERVER_ROOT_DIR, 'log\\server.log', log)
                print(log)
            self.server.header(self.conn, self.result)
        return self.pwd
