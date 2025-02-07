from core._get import Get
from core._put import Put
from core._pwd import Pwd
from core._cd import Cd
from core._sys_cmd import SysCmd
from core._dir import Dir
from core._del import Del
from core._mkdir import Mkdir
from core._set import Set


class Features:
    def __init__(self, server, username, conn, pwd, total_quotation_dic):
        # self.sys_obj = SysCmd(' '.join(cmds), server, conn)  # 运行系统命令
        self.conn = conn
        self.server = server
        self.username = username
        self.pwd = pwd
        self.total_quotation_dic = total_quotation_dic
        self.cmds = None

    def find(self, cmd_header_dic, cmds):
        self.cmds = cmds
        func_name = '_%s' % self.cmds[0]
        if hasattr(self, func_name):
            func = getattr(self, func_name)
            func(cmd_header_dic)

    def _get(self, *args):
        obj = Get(self.cmds, self.server, self.conn, self.username, args[0])
        obj.run()

    def _put(self, *args):
        obj = Put(self.cmds, self.server, self.conn, self.username, args[0])
        obj.run()

    def _pwd(self, *args):
        obj = Pwd(self.server, self.conn, self.pwd)
        obj.run()

    def _cd(self, *args):
        obj = Cd(self.cmds, self.server, self.conn, self.pwd, self.username)
        self.pwd = obj.run()  # 每变更当前目录就要改变以下self.pwd的参数

    def _dir(self, *args):
        obj = Dir(self.cmds, self.server, self.conn, self.pwd)
        obj.run()

    def _del(self, *args):
        obj = Del(self.cmds, self.server, self.conn, self.pwd, self.username)
        obj.run()

    def _mkdir(self, *args):
        obj = Mkdir(self.cmds, self.server, self.conn, self.pwd, self.username)
        obj.run()

    def _set(self, *args):
        obj = Set(self.cmds, self.server, self.conn, self.username, self.total_quotation_dic)
        obj.run()
