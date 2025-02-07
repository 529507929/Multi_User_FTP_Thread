import os
import hashlib
from core.progress_bar import ProgressBar
from conf import settings


class Put:
    def __init__(self, cmds, client):
        self.cmds = cmds
        self.client = client
        self.socket = self.client.socket

    def run(self):
        if len(self.cmds) < 2:
            return
        filename = self.cmds[1]
        user_share_dir = settings.SHARE_DIR
        send_size = 0

        # 命令发送
        cmd_header_dic = {
            'cmd': ' '.join(self.cmds),
        }
        self.client.header(self.socket, cmd_header_dic)
        # self.client.send_cmd(cmd_header_dic)  # 发送cmd到server

        # 接收断点续传信息
        undo_dic = self.client.unheader(self.socket)

        # 断点续传选择
        is_undo_file = False  # 记录是否断点传输的数据
        undo_file = undo_dic[self.client.username]['put']
        if undo_file:
            for name in undo_file:
                file_info = undo_file[name]
                print('%s \ttotal %d \tsend %d \trename %s' % (name, file_info[1], file_info[2], file_info[3]))
            while True:
                continue_choice = input('Whether to undo file transfer?(Y/N)\n>>: ').strip()
                if continue_choice.lower() == 'y':
                    while True:  # 判断是否有该文件的循环
                        file_choice = input('Choice undo file transfer.\n>>: ').strip()
                        if file_choice in list(undo_file.keys()):
                            self.cmds[1] = file_choice
                            filename = file_choice
                            is_undo_file = True  # 选择需要继续传输的文件后，变为True
                            break
                        else:
                            print('Not %s, please choose again.' % file_choice)
                    send_size = undo_dic[self.client.username]['put'][file_choice][2]
                    self.client.header(self.socket, is_undo_file)
                    self.client.header(self.socket, file_choice)
                    break
                elif continue_choice.lower() == 'n':
                    self.client.header(self.socket, is_undo_file)
                    break
                else:
                    print('Only input Y/N.')

        # 判断是否为文件，put只能传输文件
        is_dir = False
        if not os.path.isfile('%s/%s' % (user_share_dir, filename)):
            is_dir = True
            self.client.header(self.socket, is_dir)
            print('Only put file.')
            return
        elif os.path.getsize('%s/%s' % (user_share_dir, filename)) > self.client.usable_quotation:
            self.client.header(self.socket, True)
            print('Space is not enough.')
        else:
            self.client.header(self.socket, is_dir)

        """ 传输准备 """
        with open('%s/%s' % (user_share_dir, filename), 'rb') as f:
            file_md5 = hashlib.md5(f.read())
        header_dic = {
            'filename': filename,
            'md5': file_md5.hexdigest(),
            'file_size': os.path.getsize('%s/%s' % (user_share_dir, filename))
        }
        self.client.header(self.socket, header_dic)

        # 是否已经存在与Server上，是的话直接秒传
        is_has_file = self.client.unheader(self.socket)
        if is_has_file and not is_undo_file:
            compare_md5_result = self.client.unheader(self.socket)
            if compare_md5_result is True:
                progress_bar = ProgressBar(header_dic['file_size'], header_dic['file_size'])
                progress_bar.run()
                return

        """ 开始传输 """
        with open('%s/%s' % (user_share_dir, filename), 'rb') as f:
            f.seek(send_size)
            for line in f:
                self.socket.send(line)
                send_size += len(line)
                progress_bar = ProgressBar(send_size, header_dic['file_size'])
                progress_bar.run()

        check_result = self.client.unheader(self.socket)
        if is_undo_file is True:
            # 记录日志
            log = '%s again upload completed.' % '%s/%s' % (user_share_dir, filename)
            self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
            print('%s again upload completed.' % filename)
        elif check_result:
            # 记录日志
            log = '%s upload completed.' % '%s/%s' % (user_share_dir, filename)
            self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
            print('%s upload completed.' % filename)
        else:
            # 记录日志
            log = '%s upload failed.' % '%s/%s' % (user_share_dir, filename)
            self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
            print('%s upload failed.' % filename)
