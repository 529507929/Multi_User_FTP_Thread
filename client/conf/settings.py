import socket
import os


ADDRES_FAMILY = socket.AF_INET
ADDRESS_TYPE = socket.SOCK_STREAM
MAX_RECV = 1024
HOST = '127.0.0.1'
PORT = 8080
DOWNLOADS_DIR = r'G:\luffy\Project\Multi_User_FTP_Thread\client\downloads'
SHARE_DIR = r'G:\luffy\Project\Multi_User_FTP_Thread\client\share'
CLIENT_ROOT_DIR = '\\'.join(os.getcwd().split('\\')[:-1])