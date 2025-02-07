import hashlib
import os
from conf import settings


class Put:
    def __init__(self, cmds, server, conn, username, cmd_header_dic):
        self.cmds = cmds
        self.server = server
        self.conn = conn
        self.cmd_header_dic = cmd_header_dic
        self.username = username

    def run(self):
        user_recv_dir = '%s/%s/%s' % (settings.HOME_DIR, self.username, 'recv')
        mode = 'ab'
        is_undo_file = False
        filename = self.cmds[1]  # 如果断点续传选择没有改变则和Client的同名
        file_dir = '%s/%s' % (user_recv_dir, filename)  # 没有改名的原目录
        rec_size = 0  # 已经接受了的文件大小
        rename = None

        # 发送断点续传信息
        undo_dic = self.server.get_undo(self.username, settings.SERVER_ROOT_DIR, 'log\\undo.log')
        self.server.header(self.conn, undo_dic)

        # 断点续传选择
        undo_file = undo_dic[self.username]['put']
        if undo_file:
            is_undo_file = self.server.unheader(self.conn)
            if is_undo_file:
                filename = self.server.unheader(self.conn)
                rec_size = undo_file[filename][2]

                # 判断有无改名
                # is_setfilename = undo_file[filename][3]
                if undo_file[filename][3] is None:
                    file_dir = '%s/%s' % (user_recv_dir, filename)
                else:
                    file_dir = '%s/%s' % (user_recv_dir, undo_file[filename][3])
                    print(file_dir)
            else:
                mode = 'wb'

        # 判断上传来的数据是否是文件夹
        is_error = self.server.unheader(self.conn)  # 客户端返回上传的数据是否符合要求 True代表不符合
        if is_error:  # 如果是文件夹则停止put程序的运行
            # 记录日志
            log = '%s try put not file class to server.' % self.username
            self.server.wri_log(settings.SERVER_ROOT_DIR, 'log\\server.log', log)
            print(log)
            return

        """ 正常上传流程 """
        header_dic = self.server.unheader(self.conn)
        file_md5 = header_dic['md5']
        if is_undo_file is True:
            total_size = undo_file[filename][1]
        else:
            total_size = header_dic['file_size']

        # 检查文件是否已经存在
        num = 0
        self.server.header(self.conn, os.path.exists(file_dir))
        while os.path.exists(file_dir) and not is_undo_file:
            # 判断文件是否已经存在，如果在的话可以秒传
            with open(file_dir, 'rb') as f:
                server_file_md5 = hashlib.md5(f.read()).hexdigest()
            if header_dic['md5'] == server_file_md5:
                self.server.header(self.conn, True)  # MD5一样的话就返回True
                return
            else:
                self.server.header(self.conn, False)

            num += 1
            rename_list = filename.split('.')  # 这里重命名的文件名是保存到本地的文件名
            rename_list[0] += '(%d)' % num
            rename = '.'.join(rename_list)
            file_dir = '%s/%s' % (user_recv_dir, rename)
            mode = 'wb'

        with open(file_dir, mode) as f:
            while rec_size < total_size:
                try:
                    line = self.conn.recv(settings.MAX_RECV)
                    f.write(line)
                    rec_size += len(line)
                except ConnectionResetError:
                    # 与客户端连接断开，记录断点续传信息
                    undo_dic[self.username]['put'][filename] = [file_dir, total_size, rec_size, rename]
                    self.server.set_undo(settings.SERVER_ROOT_DIR, 'log\\undo.log', undo_dic)

                    # 记录日志
                    log = '%s put %s interrupt.' % (self.username, file_dir)
                    self.server.wri_log(settings.SERVER_ROOT_DIR, 'log\\server.log', log)
                    print(log)
                    return
            else:
                if is_undo_file is True:
                    del undo_dic[self.username]['put'][filename]
                    self.server.set_undo(settings.SERVER_ROOT_DIR, 'log\\undo.log', undo_dic)
                    # 记录日志
                    log = '%s put undo file %s.' % (self.username, file_dir)
                    self.server.wri_log(settings.SERVER_ROOT_DIR, 'log\\server.log', log)
                    print(log)

        # MD5验证
        print(file_dir)
        with open(file_dir, 'rb') as f:
            put_file_md5 = hashlib.md5(f.read()).hexdigest()
        check_resutl = False
        if file_md5 == put_file_md5:
            check_resutl = True
        else:
            os.remove(file_dir)
        self.server.header(self.conn, check_resutl)
