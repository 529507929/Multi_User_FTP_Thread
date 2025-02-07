import subprocess


class SysCmd:
    def __init__(self, cmd, server, conn):
        self.cmd = cmd
        self.server = server
        self.conn = conn

    def run(self):
        """
        运行系统命令
        :return:
        """
        print(self.cmd)
        obj = subprocess.Popen(self.cmd, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdout = obj.stdout.read()
        stderr = obj.stderr.read()
        header_dic = {
            'md5': 'xxxxdxxx',
            'total_size': len(stdout) + len(stderr)
        }
        self.server.header(self.conn, header_dic)
        self.conn.send(stdout)
        self.conn.send(stderr)
