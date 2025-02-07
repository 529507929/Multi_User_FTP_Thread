import hashlib
import os
import datetime
from core.progress_bar import ProgressBar
from core.undo import Undo
from conf import settings


class Get:
    def __init__(self, cmds, client):
        self.cmds = cmds
        self.client = client
        self.socket = self.client.socket
        self.undo = {}

    def run(self):
        if len(self.cmds) < 2:
            print('cmd is error')
            return
        undo_dic = self.client.get_undo(settings.CLIENT_ROOT_DIR, 'log\\undo.log')
        undo_file = undo_dic[self.client.username]['get']
        cmd_header_dic = {
            'cmd': ' '.join(self.cmds),  # get 1.mp4 1.mp4一定是Server的文件名
            'done_size': 0  # 用于记录断点续传已经完成的数据大小
        }
        is_undo_file = False  # 记录是否断点传输的数据
        file_choice = None  # 断点续传选择的本地文件名

        # 断点续传选择
        if undo_file:
            for filename in undo_file:
                file_info = undo_file[filename]
                print('%s\ttotal %d\trecv %d' % (filename, file_info[1], cmd_header_dic['done_size']))
            while True:
                continue_choice = input('Whether to undo file transfer?(Y/N)\n>>: ').strip()
                if continue_choice.lower() == 'y':
                    while True:  # 判断是否有该文件的循环
                        file_choice = input('Choice undo file transfer.\n>>: ').strip()
                        if file_choice in list(undo_file.keys()):
                            self.cmds[1] = undo_file[file_choice][2]  # 传输到Server的filename
                            is_undo_file = True  # 选择需要继续传输的文件后，变为True
                            break
                        else:
                            print('Not %s, please choose again.' % file_choice)
                    cmd_header_dic['cmd'] = ' '.join(self.cmds)
                    cmd_header_dic['done_size'] = os.path.getsize(r'%s\%s' % (settings.DOWNLOADS_DIR, file_choice))
                    self.client.send_cmd(cmd_header_dic)  # 发送命令道server
                    break
                elif continue_choice.lower() == 'n':
                    self.client.send_cmd(cmd_header_dic) # 发送命令道server
                    break
                else:
                    print('Only input Y/N.')
        else:  # 如果没有数据则进行正常的下载
            self.client.send_cmd(cmd_header_dic)

        has_file = self.client.unheader(self.socket)
        if not has_file:
            print('Not this file.')
            return

        """ 正常流程下的下载代码 """
        if is_undo_file is True:
            filename = file_choice  # 如果是断点续传那就需要更改为本地保存的文件名
        else:
            filename = '%s.%s' % (self.cmds[1],datetime.datetime.now().microsecond)  # 这里的文件名是保存在本地的临时名称
        user_downloads_dir = settings.DOWNLOADS_DIR
        file_dir = '%s/%s' % (user_downloads_dir, filename)
        header_dic = self.client.unheader(self.socket)
        file_md5 = header_dic['md5']
        total_size = header_dic['file_size']
        mode = 'ab'
        undo_dic_fun = Undo(self.client,'get',filename,undo_dic)
        undo_dic_fun.run(file_dir,total_size,self.cmds)

        # 检查是否重名
        while os.path.exists(file_dir) and not is_undo_file:
            exists_choice = input('File already exists, Y --> rename, N --> cover.\n>>: ').strip()
            if exists_choice.lower() == 'y':
                filename = input('Input new file name.\n>>: ').strip()  # 这里重命名的文件名是保存到本地的文件名
                file_dir = '%s/%s' % (user_downloads_dir, filename)
            elif exists_choice.lower() == 'n':
                mode = 'wb'
                break
            else:
                print('Only input Y/N.')

        with open(file_dir, mode) as f:
            recv_size = cmd_header_dic['done_size']
            while recv_size < total_size:
                try:
                    line = self.socket.recv(settings.MAX_RECV)
                    f.write(line)
                    recv_size += len(line)
                    progress_bar = ProgressBar(recv_size, total_size)
                    tran_result = progress_bar.run()
                    if tran_result is True:
                        # if is_undo_file:  # 如果是断点续传的文件则删除记录
                        del undo_dic[self.client.username]['get'][filename]
                        self.client.set_undo(settings.CLIENT_ROOT_DIR, 'log\\undo.log', undo_dic)
                        # 记录日志
                        log = '%s download complete.' % filename
                        self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
                        print(log)
                except ConnectionResetError:
                    # print('\n', end='')
                    # undo_dic[self.client.username]['get'][filename] = [file_dir, total_size, self.cmds[1]]
                    # self.client.set_undo(settings.CLIENT_ROOT_DIR, 'log\\undo.log', undo_dic)
                    exit('\nDisconnect from server.')

        with open(file_dir, 'rb') as f:
            download_file_md5 = hashlib.md5(f.read()).hexdigest()

        if download_file_md5 == file_md5:  # 校验下载文件的MD5值，并提示相关验证结果
            # 记录日志
            log = 'Check MD5 done to %s' % file_dir
            self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
            print('Check MD5 done to %s.' % filename)

            # 下载完成 md5验证通过 将临时名称修改为真正的名称
            filename_list = filename.split('.')
            real_filename = '.'.join(filename_list[:-1])
            os.replace(file_dir,r'%s/%s' % (user_downloads_dir, real_filename))
        else:
            # 记录日志
            log = 'MD5 is incorrect to %s' % file_dir
            self.client.wri_log(settings.CLIENT_ROOT_DIR, 'log\\client.log', log)
            print('MD5 is incorrect to %s.' % filename)
