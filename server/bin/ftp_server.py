import sys,os

# 添加环境变量
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


if __name__ == '__main__':  # 当手动调用的时候才会执行，当被当作模块导入时不会被执行

    from core import management

    argv_parser = management.ManagementTool(sys.argv)
    argv_parser.execute()