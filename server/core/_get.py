import os
import hashlib
from conf import settings


class Get:
    def __init__(self, cmds, server, conn, username, cmd_header_dic):
        self.cmds = cmds
        self.server = server
        self.conn = conn
        self.cmd_header_dic = cmd_header_dic
        self.username = username

    def run(self):
        filename = self.cmds[1]
        user_share_dir = '%s/%s/%s' % (settings.HOME_DIR, self.username, 'share')
        file_dir = '%s/%s' % (user_share_dir, filename)

        if os.path.exists(file_dir):  # 判断服务器中是否有该文件
            self.server.header(self.conn, True)
        else:
            self.server.header(self.conn, False)
            return

        done_size = 0
        if self.cmd_header_dic['done_size'] != 0:
            done_size = self.cmd_header_dic['done_size']

        with open(file_dir, 'rb') as f:
            file_md5 = hashlib.md5(f.read())

        header_dic = {
            'filename': filename,
            'md5': file_md5.hexdigest(),
            'file_size': os.path.getsize(file_dir)
        }

        self.server.header(self.conn, header_dic)
        with open(file_dir, 'rb') as f:
            f.seek(done_size)  # 根据Client传输过来的以传输的数据大小来移动指针
            for line in f:
                self.conn.send(line)

        # 记录日志
        log = '%s get %s.' % (self.username, file_dir)
        self.server.wri_log(settings.SERVER_ROOT_DIR, 'log\\server.log', log)
        print(log)
