import socket
import struct
import json
import os
from conf import settings


class ServerSocket:
    address_family = settings.ADDRES_FAMILY
    address_type = settings.ADDRESS_TYPE
    is_reuse_address = settings.IS_REUSE_ADDRESS
    max_listen = settings.MAX_LISTEN
    max_recv = settings.MAX_RECV

    def __init__(self, server_address, bind_and_active=True):
        self.server_address = server_address
        self.socket = socket.socket(self.address_family, self.address_type)
        if bind_and_active:
            try:
                self.bind()
                self.listen()
            except Exception:
                self.socket.close()
                raise

    def bind(self):
        if self.is_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def listen(self):
        self.socket.listen(self.max_listen)

    def accept(self):
        return self.socket.accept()

    def recv(self):
        self.socket.recv(self.max_recv)

    def send(self, msg):
        self.socket.send(msg)

    def close(self):
        self.socket.close()

    def header(self, conn, header_info):
        header_json = json.dumps(header_info)
        header_bytes = header_json.encode('utf-8')
        conn.send(struct.pack('i', len(header_bytes)))
        conn.send(header_bytes)

    def unheader(self, conn):
        obj = conn.recv(4)
        header_size = struct.unpack('i', obj)
        header_bytes = conn.recv(header_size[0])
        header_json = header_bytes.decode('utf-8')
        header_info = json.loads(header_json)
        return header_info

    def path_process(self, new_path, pwd):
        new_path_list = new_path.split('\\')
        comple_path_list = pwd.split('\\')
        if os.path.isabs(new_path):  # 识别是否绝对路径
            comple_path = new_path
        else:
            comple_path_list.extend(new_path_list)
            comple_path = '\\'.join(comple_path_list)
        return comple_path

    def is_file(self, path):
        if os.path.isfile(path):
            return True
        elif os.path.isdir(path):
            return False

    def wri_log(self, root_dir, log_dir, log):
        new_log_dir = os.path.join(root_dir, '%s.new' % log_dir)
        old_log_dir = os.path.join(root_dir, log_dir)
        f_log = open(old_log_dir, 'r', encoding='utf-8')
        new_f_log = open(new_log_dir, 'w', encoding='utf-8')
        for line in f_log:
            new_f_log.write(line)
        f_log.close()
        new_f_log.write(log)
        new_f_log.close()
        os.replace(new_log_dir, old_log_dir)

    def get_undo(self, username, root_dir, log_dir):
        undone_log_dir = os.path.join(root_dir, log_dir)
        if os.path.getsize(undone_log_dir) == 0:  # 当字典为空时，输入初始json {}
            with open(undone_log_dir, 'w') as f:
                dic = {}
                json.dump(dic, f)
        with open(undone_log_dir, 'r') as f:  # 读取文件中的字典
            dic = json.load(f)
            if username not in list(dic.keys()):  # 判断有无该用户名
                dic[username] = {'put': {}}
                with open(undone_log_dir, 'w') as fw:  # 没有则写入
                    json.dump(dic, fw)

        # if os.path.getsize(undone_log_dir) == 0:
        #     with open(undone_log_dir, 'w') as f:
        #         dic = {
        #             username: {
        #                 'put': {}
        #             }
        #         }
        #         json.dump(dic, f)
        # else:
        #     with open(undone_log_dir, 'r') as f:
        #         dic = json.load(f)
        return dic

    def set_undo(self, root_dir, log_dir, undone_dic):
        undone_log_dir = os.path.join(root_dir, log_dir)
        with open(undone_log_dir, 'w') as f:
            json.dump(undone_dic, f)
            f.flush()
