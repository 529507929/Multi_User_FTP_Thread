from conf import settings


class Cd:
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
        if self.new_path == '..':
            old_path = self.client.unheader(self.socket)
            old_path_list = old_path.split('\\')
            if old_path_list[-1] == self.client.username:
                # 记录日志
                log = 'Insufficient permissions, unable to return to previous level.'
                self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
                print(log)
        elif self.new_path:
            result = self.client.unheader(self.socket)
            if not result:
                # 记录日志
                log = 'Not this path or insufficient permissions, unable to return to previous level.'
                self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
                print(log)
        else:
            # 记录日志
            log = 'cmd is error'
            self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
            print(log)
