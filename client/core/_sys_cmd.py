from conf import settings


class SysCmd:
    def __init__(self, cmds, client):
        self.cmds = cmds
        self.client = client
        self.socket = self.client.socket

    def run(self):
        cmd_header_dic = {'cmd': ' '.join(self.cmds)}
        self.client.send_cmd(cmd_header_dic)
        header_dic = self.client.unheader(self.socket)
        total_size = header_dic['total_size']
        recv_size = 0
        recv_info = b''
        while recv_size < total_size:
            recv_info += self.socket.recv(settings.MAX_RECV)
            recv_size = len(recv_info)
        print(recv_info.decode('gbk'))  # 使用windows系统所以解析为gbk
