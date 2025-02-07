

class Pwd:
    def __init__(self, cmds, client):
        self.cmds = cmds
        self.client = client
        self.socket = self.client.socket

    def run(self):
        cmd_header_dic = {'cmd': ' '.join(self.cmds)}
        self.client.send_cmd(cmd_header_dic)
        now_dir = self.client.unheader(self.socket)
        print(now_dir)
