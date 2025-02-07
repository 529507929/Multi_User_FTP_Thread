from conf import settings
from conf.account import account
import json


class Set:
    def __init__(self, cmds, server, conn, username, total_quotation_dic):
        self.cmds = cmds
        self.server = server
        self.conn = conn
        self.username = username
        self.total_quotation_dic = total_quotation_dic

    def run(self):
        """
        命令运行方法
        :return:
        """
        option = self.cmds[1]
        parameter = float(self.cmds[2])
        quotation_options = ['-q', '--quotation']
        if option in quotation_options:
            self._quotation(parameter)
        else:
            print('%s input %s option is bad.' % (self.username, option))

    def _quotation(self, parameter):
        """
        用户设置使用容量
        :return:
        """
        try:
            self.total_quotation_dic[self.username] = parameter
            with open(r'%s\%s\%s' % (settings.SERVER_ROOT_DIR,'conf','quotation_db'),'w') as f:
                json.dump(self.total_quotation_dic, f)
            log = '%s change quotation to %f MB!' % (self.username, parameter)
            self.server.wri_log(settings.SERVER_ROOT_DIR, 'log\\server.log', log)
            print(log)
            self.server.header(self.conn, True)
        except Exception as e:
            log = '%s change quotation is false! --> %s' % (self.username, e)
            self.server.wri_log(settings.SERVER_ROOT_DIR, 'log\\server.log', log)
            print(log)
            self.server.header(self.conn, False)
