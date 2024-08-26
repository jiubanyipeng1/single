# -*- coding: utf8 -*-
"""
作者: 玖伴一鹏
日期: 2024-08-11
注意事项：
    1. 每天凌晨2类会执行检查一次(暂为启用)
    2. 文件夹的操作（删除、移动等操作） 不会触发服务端的更新，仅操作文件会触发
待完成：
    1. 但由于Windows分区的情况，无法进行多个磁盘文件的监视，只能使用多个客户端进行
    2. 上传单个文件使用多线程没有做好并发的准备，暂时关闭
    3. 用户许可过期重新登录
更新：
    1. 删除用户自定义日志路径，默认在当前的路径下
    2. 新增排除文件夹，该文件夹下的文件排除，默认情况下会将日志文件夹排除
    3. 移除多线程，增加客户端的稳定性
    4. 登录功能
    5. 获取文件添加许可凭证

转为exe程序：pyinstaller -F -n monitor_file_C -i peng.ico  monitor_file_C.py
"""
import os
from time import sleep
import logging
import datetime
from requests import post, RequestException
from cryptography.fernet import Fernet
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from schedule import every, run_pending
from json import load


# 读取客户端配置文件
def load_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = load(file)
        return data
    except FileNotFoundError:
        logging.error(f"读取文件：{file_path} 不存在")
        return None
    except Exception as e:
        logging.info(f"读取服务器: {e}")
        return None


# 加密函数
def encrypt(filename, token):
    """ 通用加密函数
        :param filename: 文件名
        :param token: 用户登录成功的凭证
        :格式：用户名_当前年月日_文件名称
        :return: 加密成功后的字符串
        """
    date = datetime.datetime.now().strftime("%Y%m%d")
    secret_key = f'{USERNAME}_{date}_{filename}'
    # 加密密钥
    encrypted_secret_key = Fernet(token).encrypt(secret_key.encode())
    return encrypted_secret_key


def login(data):
    """
    客户端登录
    如果登录失败会等待 60*登录次 秒后继续进行登录，经过五次将退出函数
    :param data: 登录账号密码的数据字典
    :return: bool 布尔类型
    """
    url = SERVER_URL + '/login'
    retries = 0   # 请求次数
    max_retries = 5  # 最大请求次数
    retry_delay = 0  # 等待时间
    while retries < max_retries:
        try:
            visit = post(url, data=data, timeout=30)
            if visit.status_code == 200:
                logging.info(f'用户：{USERNAME}  登录成功！')
                user_data['token'] = visit.json()['token']
                del user_data['password']   # 删除缓存内的密码
                return True
        except RequestException as e:
            logging.info(f"客户端登录，请求异常: {e}")
            retries += 1
            if retries < max_retries:
                logging.info(f"等待 {retry_delay * retries} 秒后重试...")
                sleep(retry_delay * retries)
            else:
                logging.error("登录请求达到最大重试次数，不再重试。")
                return False
        except Exception as e:
            logging.debug(f"未知错误！ {e}")
            return False


# 文件夹分离
def get_relative_path(absolute_path):
    """
    根据文件的绝对路径得出相对路径和文件名的分离
    从文件的绝对路径中获取相对路径。
    :param absolute_path: 文件的绝对路径
    :return: (相对路径文件夹, 相对路径文件名, 文件名) 的元组
    """
    directory, filename = os.path.split(absolute_path)
    relative_path = os.path.relpath(directory, base_directory)
    # 将反斜杠替换为正斜杠
    relative_path = relative_path.replace('\\', '/').replace("//", '/')
    # 如果目录为空，添加 '/' 前缀
    if not relative_path or relative_path == '.':
        relative_path = '/'
        relative_filename = relative_path + filename
    else:
        relative_path = '/' + relative_path
        relative_filename = relative_path + '/' + filename
    return relative_path, relative_filename, filename


# 检查本地文件是否可以正常上传
def check_and_upload(folder_path):
    """
    检查本地文件是否可以正常上传
    :param folder_path: 本地文件的绝对路径
    :return:  无返回，满足条件直接运行 upload_file
    """
    wait_time = 1  # 先等待1秒后再去检测
    while True:
        sleep(wait_time)
        if not os.path.exists(folder_path):
            # 这种情况也可能是刚创建但马上改名了
            # logging.info(f"{date} 文件 {filepath} 已经不存在，放弃上传。")  # 减少日志量
            return False
        try:
            with open(folder_path, 'a+'):
                pass
            relative_path, relative_filename, filename = get_relative_path(folder_path)
            is_not_file = check_file(relative_filename, filename)
            if is_not_file['mes']:
                add_token = is_not_file['add_token']
                logging.info(f'服务端无：{relative_filename}，开始上传...')
                upload_file(folder_path, relative_filename, filename, add_token)
                return True
            # logging.error(is_not_file)  减少日志，一般这里返回的都是 文件存在
        except IOError:
            logging.error(f"文件 {folder_path} 正在被使用或权限不足，等待 {wait_time} 秒后重试。")
            wait_time += 3  # 第x轮 增加等待时间
            if wait_time > 12:
                logging.error(f"文件 {folder_path} 在等待 12 秒后仍然不可用，放弃上传。")
                return False


# 初始化检查本地存在文件服务器没有存在情况
def check_local_file():
    try:
        logging.info(f'服务器地址：{SERVER_URL} 正在检测服务端的无文件情况...')
        for root, dirs, files in os.walk(base_directory):
            if not dirs and not files:
                continue

            if any(excluded_dir in root for excluded_dir in excluded_dirs):
                logger.info(f"目录排除: {root}")
                continue  # 跳过这个目录及其子目录

            for file in files:
                folder_path = os.path.join(root, file)  # 当前文件的绝对路径 含文件名
                check_and_upload(folder_path)

        logging.info(f'服务端已有全部本地文件！开始监听本地新文件情况...')
        return True
    except Exception as e:
        logging.error(f'报错：{str(e)}')
        return False


# 验证服务器是否存在文件
def check_file(relative_path, filename):
    """
    验证服务器是否存在文件，不存在则返回许可凭证
    :param relative_path:  本地相对路径文件夹
    :param filename:  本地相对路径文件名
    :return: {'mes':True,'add_token':add_token}
    """
    try:
        url = SERVER_URL + '/check'
        data = {'username': USERNAME, 'token': user_data['token'], 'path': relative_path, 'filename': filename}
        check_path = post(url, data=data, timeout=30)
        if check_path.status_code == 200:
            add_token = check_path.json()['add_token']
            return {'mes': True, 'add_token': add_token}
        else:
            return {'mes': False, 'error': check_path.json()}
    except Exception as e:
        return {'mes': False, 'error': str(e)}


# 上传文件
def upload_file(absolute_path, relative_path, filename, add_token, operate_type='add', former=''):
    """
    上传文件
    :param absolute_path: 本地文件的绝对路径
    :param relative_path: 本地文件的相对路径
    :param filename:  文件名
    :param add_token:  添加文件的许可凭证
    :param operate_type:  操作类型，默认为添加
    :param former:  旧文件的相对路径文件名
    :return: {'mes':True,'info':}
    """
    url = SERVER_URL + '/upload'
    try:
        with open(absolute_path, 'rb') as f:
            files = {'file': (filename, f)}
            # 由于验证是通过日期进行加密，可能会存在刚好跨天的情况，所以执行两次
            logging.info(f'开始上传文件：{absolute_path} ...')
            token_key = encrypt(filename, user_data['token'])
            data = user_data
            data['token_key'] = token_key
            data['filename'] = filename
            data['path'] = relative_path
            data['type'] = operate_type
            data['add_token'] = add_token
            data['former'] = former
            # 注意：这里仅等待60秒，如果是外网或文件太大请自己设置更大：timeout=要设置的时间
            response = post(url, files=files, data=data, timeout=60)
            if response.status_code == 200:
                logging.info(f"{absolute_path} 上传成功！")
                return {'mes': True, 'info': response.json()}
        # logging.error(f"{absolute_path} 上传失败！\n {response.json()}")
        print(f'\033[31m\033[47m {response.json()["error"]} \033[0m')
        return {'mes': False, 'info': response.json()}
    except Exception as e:
        logging.error(f"服务器连接超时或无法打开文件 {absolute_path}: {e}")
        return False


# 文件系统事件处理器
class FileCreatedHandler(FileSystemEventHandler):
    def __init__(self, exclude_dir):
        super().__init__()
        self.exclude_dirs = (exclude_dir,)

    def is_excluded(self, event):
        # 检查事件是否来自需要排除的文件夹
        for path_dir in self.exclude_dirs:
            if event.src_path.startswith(path_dir):
                return True
        return False

    # 文件创建操作
    def on_created(self, event):
        if not self.is_excluded(event) and event.is_directory is False:
            check_and_upload(event.src_path)

    # 文件删除操作
    def on_deleted(self, event):
        if not self.is_excluded(event) and event.is_directory is False:
            print(f"文件 {event.src_path} 被删除。")

    # 文件移动操作
    def on_moved(self, event):
        if self.is_excluded(event) and event.is_directory is False:
            print(f"文件 {event.src_path} 被移动到 {event.dest_path}。")

    # 文件修改操作
    def on_modified(self, event):
        if not self.is_excluded(event) and event.is_directory is False:
            print(f"文件 {event.src_path} 被修改。")


# 监控指定目录
def monitor_folder(folder_path, exclude_dir):
    observer = Observer()
    observer.schedule(FileCreatedHandler(exclude_dir), folder_path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# 每日凌晨2点执行 check_local_file
def schedule_check_local_file():
    every().day.at("02:00").do(check_local_file)

    while True:
        run_pending()
        sleep(1)


# 设置配置相关
client_config = './client_config.json'
if not os.path.exists(client_config):
    print(f'配置文件不存在！！！！！！！')
    exit()

config_data = load_json_data(client_config)
if not config_data:
    logging.error(f'配置文件有问题')
    exit()

USERNAME = config_data.get('username', 'admin')
PASSWORD = config_data.get('password', 'password')
SERVER_URL = config_data.get('server_url', 'http://127.0.0.1:8080')
base_directory = config_data.get('client_path', './')
log_path = '/client_log'
excluded_dirs = config_data.get('excluded_dirs', [])
excluded_dirs.append(base_directory+log_path)  # 排除日志的


os.makedirs(log_path, exist_ok=True)  # 日志文件夹
os.makedirs(base_directory, exist_ok=True)  # 检测文件夹

# 用户通用的缓存数据
user_data = {
    'username': USERNAME,
    'password': PASSWORD,  # 登录成功会被删除
    'token': '',  # 登录成功凭证
}

# 配置即控制端输出也记录日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# 创建一个handler，用于写入日志文件
file_handler = logging.FileHandler(f'{log_path}/client_{datetime.datetime.now().strftime("%Y%m%d")}.txt')
file_handler.setLevel(logging.INFO)
# 再创建一个handler，用于输出到控制台
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
# 给logger添加handler
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


if __name__ == "__main__":
    # Thread(target=schedule_check_local_file).start()
    login(user_data)
    if check_local_file():
        monitor_folder(base_directory, excluded_dirs)
    else:
        logging.error(f'在初始化，在检查本地文件是否已上传服务器：失败！')
        sleep(10)
        exit()
