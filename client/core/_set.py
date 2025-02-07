import optparse
import os


class Set:
    def __init__(self, cmds, client):
        self.cmds = cmds
        self.client = client
        self.socket = self.client.socket

    def run(self):
        """
        命令格式核对方法
        :return:
        """
        if len(self.cmds) == 3:
            option = self.cmds[1]
            parameter = self.cmds[2]
            quotation_options = ['-q','--quotation']
            if option in quotation_options:
                self._quotation(parameter)
            else:
                print('%s option is bad.' % option)
                return
        else:
            print("Error: must supply size parameters\n"
                  "Usage: set [options] size\n"
                  "Size unit is MB.")
            return

    def _quotation(self, parameter):
        """
        处理用户设置使用容量
        :return:
        """
        if ''.join(parameter.split('.')).isdigit():
            quotation_header_dic = {
                'cmd': ' '.join(self.cmds)
            }
            self.client.send_cmd(quotation_header_dic)
            is_set = self.client.unheader(self.socket)
            if is_set:
                print('Set complete.')
            else:
                print('Set false.')
        else:
            print('Parameter must be floating point or integer and unit is MB.')
            return

