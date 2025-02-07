from conf import settings


class Mkdir:
    def __init__(self, cmds, client):
        self.cmds = cmds
        self.client = client
        self.socket = client.socket

    def run(self):
        cmd_header_dic = {'cmd': ' '.join(self.cmds)}
        self.client.send_cmd(cmd_header_dic)
        mkdir_result = self.client.unheader(self.socket)
        if mkdir_result is True:
            # 记录日志
            log = 'Mkdir complete.'
            self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
            print(log)
        else:
            # 记录日志
            log = 'Mkdir failure.'
            self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
            print(log)
