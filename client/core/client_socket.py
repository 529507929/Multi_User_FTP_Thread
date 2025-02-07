import socket
import struct
import json
import os
from conf import settings


class ClientSocket:
    address_family = settings.ADDRES_FAMILY
    address_type = settings.ADDRESS_TYPE
    max_recv = settings.MAX_RECV

    def __init__(self, server_address, bind_and_active=True):
        self.server_address = server_address
        self.socket = socket.socket(self.address_family, self.address_type)
        if bind_and_active:
            try:
                self.connect()
            except:
                self.socket.close()
                raise

    def connect(self):
        self.socket.connect(self.server_address)

    def close(self):
        self.socket.close()

    def send_cmd(self, dic):
        cmd_header_dic = dic
        self.header(self.socket, cmd_header_dic)

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

    def wri_log(self, root_dir, log_dir, log):
        new_log_dir = os.path.join(root_dir, '%s.new' % log_dir)
        old_log_dir = os.path.join(root_dir, log_dir)
        f_log = open(old_log_dir, 'r', encoding='utf-8')
        new_f_log = open(new_log_dir, 'w', encoding='utf-8')
        for line in f_log:
            new_f_log.write(line)
        f_log.close()
        new_f_log.write(log+'\n')
        new_f_log.close()
        os.replace(new_log_dir, old_log_dir)

    def get_undo(self, root_dir, log_dir):
        undone_log_dir = os.path.join(root_dir, log_dir)
        if os.path.getsize(undone_log_dir) == 0:
            with open(undone_log_dir, 'w') as f:
                dic = {}
                json.dump(dic, f)
        with open(undone_log_dir, 'r') as f:
            dic = json.load(f)
            if self.username not in list(dic.keys()):  # 判断用户是否已经在字典当中
                dic[self.username] = {'get': {}}  # 如果没有就添加上去
                with open(undone_log_dir, 'w') as fw:
                    json.dump(dic, fw)  # 写入到文件
        return dic  # 如果有就取出来

    def set_undo(self, root_dir, log_dir, undone_dic):
        undone_log_dir = os.path.join(root_dir, log_dir)
        with open(undone_log_dir, 'w') as f:
            json.dump(undone_dic, f)
            f.flush()
