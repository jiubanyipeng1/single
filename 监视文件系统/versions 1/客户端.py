# -*- coding: utf8 -*-
from os import makedirs, path, walk
from time import sleep
import logging
import datetime
from threading import Thread
from requests import get, post
from cryptography.fernet import Fernet
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from base64 import b64encode
from schedule import every, run_pending
from json import load
# 转为exe程序：pyinstaller -F -n 上传_客户端 -i peng.ico  上传_客户端.py
# 注意，每天凌晨2类会执行检查一次


# 读取客户端配置文件
def load_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = load(file)
        return data
    except FileNotFoundError:
        print(f"读取文件：{file_path} 不存在")
        return None
    except Exception as e:
        print(f"读取服务器: {e}")
        return None


# 加密函数
def encrypt(filename):
    """ 通用加密函数
        :param filename: 文件名
        :格式：用户名_当前年月日_文件名称
        :return:
        """
    date = datetime.datetime.now().strftime("%Y%m%d")
    secret_key = f'{USERNAME}_{date}_{filename}'
    # 加密密钥
    encrypted_secret_key = Fernet(TOKEN_KEY).encrypt(secret_key.encode())
    return encrypted_secret_key


# 构造请求头
def header(file_name, filepath='/', req_type='created', former='无'):
    """通用请求头
    :param file_name: 文件名
    :param filepath: 相对文件路径
    :param req_type: 上传的类型 --> 创建：created，删除：deleted，修改：modified，移动：moved
    :param former: 旧文件名，上传类型为创建和删除不需要，其他类型需要指定旧值
    :return:{}
    """
    token = encrypt(file_name)
    # 进行值的转化  后期改用data的方式
    encoded_filename = b64encode(file_name.encode('utf-8')).decode('utf-8')
    encoded_username = b64encode(USERNAME.encode('utf-8')).decode('utf-8')
    encoded_path = b64encode(filepath.encode('utf-8')).decode('utf-8')
    encoded_former = b64encode(former.encode('utf-8')).decode('utf-8')
    headers = {
        "Authorization": token,
        "filename": encoded_filename,
        "username": encoded_username,
        "path": encoded_path,
        "type": req_type,
        "former": encoded_former
    }
    return headers


# 文件夹分离
def get_relative_path(absolute_path):
    """
    从文件的绝对路径中获取相对路径。
    :param absolute_path: 文件的绝对路径
    :return: (相对路径, 文件名) 的元组
    """

    directory, filename = path.split(absolute_path)
    relative_path = path.relpath(directory, base_directory)
    # 将反斜杠替换为正斜杠
    relative_path = relative_path.replace('\\', '/')
    # 如果目录为空，添加 '/' 前缀
    if not relative_path or relative_path == '.':
        relative_path = '/'
    else:
        relative_path = '/' + relative_path

    return relative_path


# 获取服务器上的文件数据
def get_server_files_data():
    """ 获取服务器目前已存在文件数据接口
    : 验证成功：{'type':1,'data': data}  错误：{'type':0,'error': f'验证失败！ {present_time}'}
    :return:  以列表数据返回
    """
    # 注意，请求服务器文件默认字符串为：请求文件
    response = get(f'{SERVER_URL}/get_files_data', headers=header('请求文件'), timeout=30)
    if response.status_code == 200:
        return response.json()['data']
    else:
        logging.error(f"获取获取服务器上的文件数据失败: {response.text}")
        return []


# 检查本地文件并上传文件
def check_and_upload(file_path, filename):
    wait_time = 1  # 先等待1秒后再去检测
    filepath = path.join(file_path, filename)
    while True:
        sleep(wait_time)
        if not path.exists(filepath):
            # 这种情况也可能是刚创建但马上改名了
            # logging.info(f"{date} 文件 {filepath} 已经不存在，放弃上传。")  # 减少日志量
            break
        try:
            with open(filepath, 'a+'):
                pass
            logging.info(f"文件 {filepath} 开始上传...")
            thread = Thread(target=upload_file, args=(filepath, filename))
            thread.start()
            break
        except IOError:
            logging.info(f"文件 {filepath} 正在被使用或权限不足，等待 {wait_time} 秒后重试。")
            wait_time += 3  # 第x轮 增加等待时间
            if wait_time > 12:
                logging.error(f"文件 {filepath} 在等待 12 秒后仍然不可用，放弃上传。")
                break


# 检查本地存在文件服务器没有存在情况
def check_local_file():
    try:
        logging.info(f'正在检测服务的无文件情况...')
        print(f'服务器地址：{SERVER_URL}, 向服务器获取文件情况...')
        server_files_data = get_server_files_data()
        if not server_files_data:
            print('文件服务器数据返回空！！！')
        print('开始检查本地文件情况...')
        for root, dirs, files in walk(base_directory):
            if not dirs and not files:
                print('检测的本地文件夹内没有子文件夹和文件！')
                break

            for file in files:
                folder_path = path.join(root, file)
                relative_path = get_relative_path(folder_path)
                if relative_path == '/':
                    relative_path = relative_path + file
                else:
                    relative_path = relative_path + '/' + file
                # 文件的验证都是通过相对路径验证，后期也可以指定用户文件夹
                if relative_path not in server_files_data:
                    logging.info(f'服务端无：{relative_path}，开始上传...')
                    print(f'服务端无：{relative_path}，开始上传...')
                    upload_file(folder_path, file)

        logging.info(f'服务端已有全部本地文件！开始监听本地新文件情况...')
        print(f'服务端已有全部本地文件！开始监听本地新文件情况...')
    except Exception as e:
        print(f'报错：{str(e)}')


# 上传文件
def upload_file(absolute_path, filename):
    url = SERVER_URL + '/upload'
    file_path = get_relative_path(absolute_path)
    try:
        with open(absolute_path, 'rb') as f:
            files = {'file': (filename, f)}
            # 由于验证是通过日期进行加密，可能会存在刚好跨天的情况，所以执行两次
            print(f'开始上传文件：{absolute_path} ...')
            for i in range(2):
                # 注意：这里仅等待60秒，如果是外网或文件太大请自己设置更大：timeout=要设置的时间
                response = post(url, files=files, headers=header(filename, file_path), timeout=60)
                if response.status_code == 200:
                    logging.info(f"{absolute_path} 上传成功！")
                    return
                if i == 0:
                    sleep(3)  # 3秒后继续上传一次
            logging.error(f"{absolute_path} 上传失败！\n {response.text}")

    except Exception as e:
        logging.error(f"服务器连接超时或无法打开文件 {absolute_path}: {e}")
        print(f"服务器连接超时或无法打开文件 {absolute_path}: {e}")


# 文件系统事件处理器
class FileCreatedHandler(FileSystemEventHandler):
    # 文件创建操作
    def on_created(self, event):
        from os import path
        if not event.is_directory:
            filepath, filename = path.split(event.src_path)
            thread = Thread(target=check_and_upload, args=(filepath, filename))
            thread.start()

    # # 文件删除操作
    # def on_deleted(self, event):
    #     if not event.is_directory:
    #         print(f"文件 {event.src_path} 被删除。")
    #
    # # 文件移动操作
    # def on_moved(self, event):
    #     if not event.is_directory:
    #         print(f"文件 {event.src_path} 被移动到 {event.dest_path}。")
    #
    # # 文件修改操作
    # def on_modified(self, event):
    #     if not event.is_directory:
    #         print(f"文件 {event.src_path} 被修改。")


# 监控指定目录
def monitor_folder(folder_path):
    observer = Observer()
    observer.schedule(FileCreatedHandler(), folder_path, recursive=True)
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
if not path.exists(client_config):
    print(f'配置文件不存在！！！！！！！')
    exit()

config_data = load_json_data(client_config)
if not config_data:
    print(f'配置文件有问题')
    exit()
USERNAME = config_data.get('username', 'admin')  # 查询日志方便排查及后期账号相关验证
PASSWD = config_data.get('passwd','passwd')  # 暂时不启用
SERVER_URL = config_data.get('server_url','http://127.0.0.1:8080')
TOKEN_KEY = config_data.get('token_key','token_key').encode()  # 应该采取其它方式获取到token，后期修改为与服务端交互账号密码得到
base_directory = config_data.get('client_path', './')
log_path = config_data.get('client_logs_filepath','logs')
makedirs(log_path, exist_ok=True)  # 日志文件夹
makedirs(base_directory, exist_ok=True)  # 检测文件夹

# 配置日志
logging.basicConfig(filename=f'logs/client_{datetime.datetime.now().strftime("%Y%m%d")}.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    Thread(target=schedule_check_local_file).start()
    check_local_file()
    monitor_folder(base_directory)
