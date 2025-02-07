from conf import settings


class Del:
    def __init__(self, cmds, client):
        if len(cmds) > 1:
            self.new_path = cmds[1]
        else:
            self.new_path = None
        self.cmds = cmds
        self.client = client
        self.socket = client.socket

    def run(self):
        cmd_header_dic = {'cmd': ' '.join(self.cmds)}
        self.client.send_cmd(cmd_header_dic)
        del_result = self.client.unheader(self.socket)
        if del_result is True:
            # 记录日志
            log = 'Del complete.'
            self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
            print(log)
        elif del_result == 'not found':
            # 记录日志
            log = 'Path not found.'
            self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
            print(log)
        else:
            # 记录日志
            log = 'Del failure.'
            self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
            print(log)
