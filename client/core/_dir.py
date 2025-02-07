

class Dir:
    def __init__(self, cmds, client):
        self.cmds = cmds
        self.client = client
        self.socket = client.socket

    def run(self):
        cmd_header_dic = {'cmd': ' '.join(self.cmds)}
        self.client.send_cmd(cmd_header_dic)
        file_list = self.client.unheader(self.socket)
        if isinstance(file_list, list):
            for i in range(0, len(file_list)):
                if i+1 % 5 == 0 or i+1 == len(file_list):
                    pri_str = file_list[i] + '\n'
                else:
                    pri_str = file_list[i] + ' '
                print(pri_str, end='')
        else:
            print(file_list)
