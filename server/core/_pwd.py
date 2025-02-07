

class Pwd:
    def __init__(self, server, conn, pwd):
        self.server = server
        self.conn = conn
        self.pwd = pwd

    def run(self):
        self.server.header(self.conn, self.pwd)
