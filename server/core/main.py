from core import server_socket
from core.features import Features
from conf import settings
from conf.account import account
from threading import Thread, currentThread  # 用于测试，查看当前所在线程
import queue
import os
import json


class Main:
    """
    服务器主程序
    """
    def __init__(self, management_instance):
        self.management_instance = management_instance
        self.server = server_socket.ServerSocket((settings.HOST, settings.PORT))
        self.q = queue.Queue(settings.MAX_ACCOUNT_CONCURRENT)
        self.server_address = self.server.server_address
        self.sock = None  # 服务器的socket
        self.client_addr = None
        self.username = None
        self.password = None
        self.cmds = None

    def run(self):
        """
        主线程，等待客户端链接的方法
        接待处，迎接客户端的地方
        :return:
        """
        print('starting FTP server on %s:%s'.center(50, '-') % (settings.HOST, settings.PORT))
        while True:  # 链接循环
            conn, self.client_addr = self.server.accept()
            try:
                t = Thread(target=self.handle, args=(conn,))
                self.q.put(t)  # 每来一个客户端就put一个线程进去队列当中，如果满了后面进来的就等待着
                print(t)
                t.start()
            except Exception as e:
                print(e)
                conn.close()
                self.q.get()

        self.server.socket.close()

    def handle(self, conn):
        """
        用于处理每一个客户端的登录信息与命令信息
        服务员，每一个线程就有一个这种服务员
        :param conn: 当前线程的通道(conn)
        :return:
        """
        is_login = False  # 每个客户端链接上来一定是未登录状态
        is_login = self._auth(conn, is_login)  # 登录模块
        with open(r'%s\%s\%s' % (settings.SERVER_ROOT_DIR, 'conf', 'quotation_db'), 'r') as f:  # 读取空间配额
            total_quotation_dic = json.load(f)
        user_quotation = (self.get_dir_size(account[self.username]['home']),total_quotation_dic[self.username])  # 获取用户当前已使用容量与可使用的总容量 MB为单位
        self.server.header(conn, user_quotation)
        pwd = account[self.username]['home']  # 初始化当前目录
        func = Features(self.server, self.username, conn, pwd, total_quotation_dic)  # 初始话功能类的同时也要导入初始话变量

        while is_login:
            # print(self.q.full(),is_login,currentThread().getName())
            if is_login:
                try:
                    res = self.server.unheader(conn)
                    if not res:
                        conn.close()
                        self.q.get()
                    self.cmds = res['cmd'].split()
                    func.find(res, self.cmds)
                    # func_name = '_%s' % self.cmds[0]
                    # if hasattr(self, func_name):
                    #     func = getattr(self, func_name)
                    #     func(conn)
                except Exception as e:
                    print(e)
                    conn.close()
                    self.q.get()
                    break

    def _auth(self, conn, is_login):
        """
        登陆方法，用于处理登录信息
        :param conn: 当前线程的通道(conn)，用于与客户端通信
        :param is_login: 登录结果，初始值为False
        :return: is_login 为判断是否已经登录
        """
        while not is_login:
            try:
                account_info = self.server.unheader(conn)
                self.username = account_info[0]
                self.password = account_info[1]
                if self.username in account.keys() and self.password == account[self.username]['password']:
                    is_login = True
                    # self.server.username = self.username  # 属于username的socket
                    self.server.header(conn, is_login)  # 登录成功返回登录状态
                    print('%s is login from %s' % (self.username, self.client_addr))
                    break
                else:
                    self.server.header(conn, is_login)  # 登录失败返回登录状态
                    print('%s try login by %s, result is bad.' % (self.client_addr, self.username))
                    continue
            except ConnectionResetError:
                is_login = False
                break
        return is_login

    def get_dir_size(self, path, total_size=0):
        """
        获取目录大小
        :param path: 需要获取的目录路径
        :param total_size: 目录的总大小
        :return:
        """
        file_list = os.listdir(path)
        for filename in file_list:
            path_tmp = os.path.join(path,filename)
            if os.path.isfile(path_tmp):
                file_size = os.path.getsize(path_tmp)
                total_size += file_size
            elif os.path.isdir(path_tmp):  # 当是文件夹的时候递归计算文件夹当中的文件大小
                total_size = self.get_dir_size(path_tmp, total_size)
        return total_size  # 字节(byte)为单位
