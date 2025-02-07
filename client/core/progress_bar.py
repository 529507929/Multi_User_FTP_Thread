import sys


class ProgressBar:
    def __init__(self, tran_size, total_size):
        self.tran_size = tran_size
        self.total_size = total_size

    def run(self):
        part = self.total_size / 50  # 2% 数据的大小
        count = int(self.tran_size / part)
        # sys.stdout.write('\r')  # 将指针调回开头
        print('\r', end='')
        # sys.stdout.write('[%-50s]%.2f%%' % (('>' * count), (self.tran_size / self.total_size) * 100))
        print('[%-50s]%.2f%%' % (('>' * count), (self.tran_size / self.total_size) * 100), end='', flush=True)
        # sys.stdout.flush()  # python2 为了强制显示到屏幕上

        if self.tran_size >= self.total_size:
            # sys.stdout.write('\n')  # 在结束的时候在结尾加上'\n'换行
            print('\n', end='')
            return True
