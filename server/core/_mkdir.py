import os
from conf import settings


class Mkdir:
    def __init__(self, cmds, server, conn, pwd, username):
        if len(cmds) > 1:
            self.new_path = cmds[1]
        else:
            self.new_path = None
        self.cmds = cmds
        self.server = server
        self.conn = conn
        self.pwd = pwd
        self.username = username

    def run(self):
        comple_path = self.server.path_process(self.new_path, self.pwd)
        os.makedirs(comple_path)

        # 记录日志
        log = '%s make dir %s' % (self.username, comple_path)
        self.server.wri_log(settings.SERVER_ROOT_DIR, 'log\\server.log', log)
        print(log)

        self.server.header(self.conn, True)
