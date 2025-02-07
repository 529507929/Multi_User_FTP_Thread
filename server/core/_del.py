import os
from conf.account import account
from conf import settings


class Del:
    def __init__(self, cmds, server, conn, pwd, username):
        if len(cmds) > 1:
            self.new_path = cmds[1]
        else:
            self.new_path = None
        self.cmds = cmds
        self.server = server
        self.conn = conn
        self.username = username
        self.pwd = pwd

    def run(self):
        account_path = account[self.username]['home']
        comple_path = self.server.path_process(self.new_path, self.pwd)
        is_file = self.server.is_file(comple_path)
        if os.path.exists(comple_path) and account_path == comple_path[:len(account_path)]:
            if is_file:
                os.remove(comple_path)
                log = '%s del file by %s' % (self.username, comple_path)
                self.server.wri_log(settings.SERVER_ROOT_DIR, 'log\\server.log', log)
                print(log)
                self.server.header(self.conn, True)
            elif not is_file:
                for root, dirs, file in os.walk(comple_path, topdown=False):  # 清空指定文件夹内的文件
                    for name in file:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(comple_path)  # 删除指定的文件夹

                log = '%s del dir by %s' % (self.username, comple_path)
                self.server.wri_log(settings.SERVER_ROOT_DIR, 'log\\server.log', log)
                print(log)
                self.server.header(self.conn, True)
            else:
                log = '%s del file find ERROR!' % self.username
                self.server.wri_log(settings.SERVER_ROOT_DIR, 'log\\server.log', log)
                print(log)
                self.server.header(self.conn, False)
        else:
            self.server.header(self.conn, 'not found')
