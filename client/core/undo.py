from conf import settings


class Undo:
    def __init__(self, client, mode, filename, undo_dic):
        self.client = client
        self.mode = mode
        self.filename = filename
        self.undo_dic = undo_dic

    def run(self,file_dir, total_size, cmds):
        self.undo_dic[self.client.username][self.mode][self.filename] = [file_dir, total_size, cmds[1]]
        self.client.set_undo(settings.CLIENT_ROOT_DIR, 'log\\undo.log', self.undo_dic)
