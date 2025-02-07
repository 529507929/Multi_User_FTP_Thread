import sys
import os

# 添加环境变量
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from core.main import Main


if __name__ == '__main__':
    start = Main()
    start.run()
