# -*- coding: utf8 -*-
"""
作者: 玖伴一鹏
日期: 2024-08-11
注意事项：
    1. Linux和windows 文件路径会存在区别，客户端和服务端都是Windows暂时不考虑
    2. 客户端与服务端数据文件，两者之间的验证在不同系统可能会出现异常(未验证！)
    3. 文件是先存到内存中再启用另外一个线程去保存
待完成：
    1. TOKEN_KEY 密钥的获取方式，使用账号密码的验证返回
    2. 文件的删、改、移没有进行处理

转为exe程序：pyinstaller -F -n 上传_服务器 -i peng.ico  上传_服务器.py
"""


from os import path, makedirs
import logging
from flask import Flask, request, jsonify
from datetime import datetime
from cryptography.fernet import Fernet
from threading import Thread
from base64 import b64decode
from json import load
app = Flask(__name__)


# 读取服务器配置文件
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


# 解密
def decrypt(authorization_header, username, filename=''):
    """
    解密函数验证
    :param authorization_header: 用户加密后的数据，传输过来的是字符串需要进行编码
    :param username: 用户名
    :param filename: 文件名
    :格式：用户名_当前年月日_文件名称
    :return:bool
    """
    date = datetime.now().strftime("%Y%m%d")
    secret_key = f'{username}_{date}_{filename}'
    decrypted_secret_key = Fernet(TOKEN_KEY).decrypt(authorization_header.encode()).decode('utf-8')
    if decrypted_secret_key == secret_key:
        return True
    else:
        return False


# 初始化或加载数据 文件
def load_data():
    try:
        with open(DATA_FILE_PATH, 'r') as file:
            return file.read()
    except Exception as e:
        logging.error(f'读取文件：{DATA_FILE_PATH}  失败！可能没有权限或文件不存在 {e}')
        return False


# 添加写入完成文件数据
def add_data(filepath):
    try:
        with open(DATA_FILE_PATH, 'a') as file:
            file.write(filepath + '\n')
            return True
    except Exception as e:
        logging.error(f'读取文件：{DATA_FILE_PATH}  失败！可能没有权限或文件不存在 {e}')
        return False


# 保存数据文件
def save_data(file_path, file_name, file_data):
    # # 类型文件验证
    # allowed_extensions = {'jpg', 'jpeg', 'png', 'pdf', 'xml'}
    # # 检查文件类型
    # if '.' in file_name:
    #     extension = file_name.rsplit('.', 1)[1].lower()
    #     if extension not in allowed_extensions:
    #         logging.error(f"文件 {file_name} 类型不被允许。")
    #         return {'type': 0, 'mes': f'文件类型 {extension} 不被允许。'}

    # 构建服务器上文件的路径
    if file_path in ('', '/'):
        file_absolute_path = path.join(server_savefile, file_name)  # 文件绝对路径
        file_relative_path = file_path + file_name  # 文件的相对路径
    else:
        file_absolute_path = path.join(server_savefile, file_path.strip('/'), file_name)
        file_relative_path = file_path + '/' + file_name  # 文件的相对路径
        server_path = server_savefile.replace('\\', '/') + file_path  # 绝对文件夹路径
        # 创建文件夹
        if not path.exists(server_path):
            makedirs(server_path, exist_ok=True)
    try:

        # 保存文件到指定路径
        with open(file_absolute_path, 'wb') as f:
            f.write(file_data)
        # 验证文件是否成功保存
        if path.exists(file_absolute_path):
            logging.info(f"文件上传：{file_absolute_path} 上传成功！")
            # 添加成功数据
            add_data(file_relative_path)
            return {'type': 1, 'mes': f'文件:{file_absolute_path} 保存完成！'}
        else:
            logging.error(f"文件:{file_absolute_path} 保存失败，文件不存在。")
            return {'type': 0, 'mes': '文件保存失败，文件不存在。'}

    except Exception as e:
        logging.error(f"无法保存文件:{file_absolute_path}: {e}")
        return {'type': 0, 'mes': str(e)}


# 触发上传处理
@app.route('/upload', methods=['POST'])
def upload_file():
    client_ip = request.remote_addr    # 记录IP地址
    try:
        if request.method == 'POST':
            token = request.headers.get('Authorization', False)
            file_name = request.headers.get('filename', False)
            username = request.headers.get('username', False)
            pfile_path = request.headers.get('path', False)
            get_type = request.headers.get('type', '')
            former = request.headers.get('former', '')

            # 验证
            if token and file_name and username and path:
                decoded_filename = b64decode(file_name).decode('utf-8')
                decoded_username = b64decode(username).decode('utf-8')
                decoded_path = b64decode(pfile_path).decode('utf-8')
                decoded_former = b64decode(former).decode('utf-8')
                if not decrypt(token, decoded_username, decoded_filename):
                    logging.error(f'文件上传_{decoded_username}:{client_ip}:验证失败，token不匹配！。 \n {request.headers} ')
                    return jsonify({'error': 'token不匹配！'}), 400
            else:
                logging.info(f'文件上传_{username}:{client_ip}:验证失败，提交的数据不完整！。\n {request.headers} ')
                return jsonify({'type': 1, 'error': '提交的数据不完整！'}), 400

            # 暂时仅做文件的新增处理，后面有时间再添加 删除、修改、移动

            file = request.files['file']
            if file.filename == '':
                return "文件名不存在", 400

            # 读取文件内容到内存中
            file_data = file.read()
            thread = Thread(target=save_data, args=(decoded_path, decoded_filename, file_data))
            thread.start()
            return jsonify({'message': f'上传完成，等待服务器处理！ '}), 200

        else:
            logging.error(f'文件上传： {client_ip}  进行请求。  \n {request.headers}  ')
            return jsonify({'error': f'请求错误！'}), 400
    except Exception as e:
        logging.debug(f'文件上传：出错！！！ \n {e}')
        return jsonify({'error': f'请求错误！{e}'}), 400


@app.route('/get_files_data', methods=['GET'])
def get_files_data():
    client_ip = request.remote_addr
    auth_header = request.headers.get('Authorization', False)
    username = request.headers.get('username', False)
    if auth_header and username:
        decoded_username = b64decode(username).decode('utf-8')
        if decrypt(auth_header, decoded_username, '请求文件'):
            logging.info(f'获取文件列表_{decoded_username}:{client_ip}:验证成功。')
            data = load_data()
            if data:
                return jsonify({'type': 1, 'data': data.split('\n')}), 200
            else:
                return jsonify({'type': 1, 'data': []}), 200
        else:
            logging.error(f'获取文件列表_{decoded_username}:{client_ip}:验证失败，auth_header验证不通过。   {request.headers} ')
            return jsonify({'type': 0, 'error': f'验证失败，auth_header验证不通过！ '}), 400
    else:
        logging.error(f'获取文件列表_{username}:{client_ip}:验证失败，没有 auth_header 或 username。')
        return jsonify({'type': 0, 'error': f'验证失败,没有 auth_header 或 username。！ '}), 400


# 配置
server_config = './server_config.json'
if not path.exists(server_config):
    print(f'配置文件不存在！！！！！！！')
    exit()

config_data = load_json_data(server_config)
if not config_data:
    print(f'配置文件有问题')
    exit()


# 数据文件
DATA_FILE_PATH = config_data.get('data_filepath', 'filesdata.txt')  # 后期改成数据库的方式
server_logs_filepath = config_data.get('server_logs_filepath', 'log')
server_savefile = config_data.get('server_save_filepath', './')
TOKEN_KEY = config_data.get('token_key', 'admin').encode()  # 应该采取其它方式获取到token，后期修改为与服务端交互账号密码得到
server_host = config_data.get('server_host', '0.0.0.0')
server_port = config_data.get('server_port', 8080)
server_flask_debug = config_data.get('server_flask_debug', True)

# 创建文件夹 和 文件
makedirs(server_logs_filepath, exist_ok=True)
makedirs(server_savefile, exist_ok=True)
if not path.exists(DATA_FILE_PATH):
    open(DATA_FILE_PATH, 'w').close()


# # 配置日志
# logging.basicConfig(filename=f'logs/server_{datetime.now().strftime("%Y%m%d")}.txt', level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')
# 配置即控制端输出也记录日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建一个handler，用于写入日志文件
file_handler = logging.FileHandler(f'{server_logs_filepath}/server_{datetime.now().strftime("%Y%m%d")}.txt')
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

if __name__ == '__main__':
    app.run(host=server_host, port=server_port, debug=server_flask_debug)
