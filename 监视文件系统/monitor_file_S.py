# -*- coding: utf8 -*-
"""
作者: 玖伴一鹏
日期: 2024-08-11
注意事项：
    1. Linux和windows 文件路径会存在区别，客户端和服务端都是Windows暂时不考虑Linux
    2. 文件是先存到内存中再启用另外一个线程去保存，因此越大的文件需要的内存越大

待完成：
    1. 将功能合拼到一个类中
    2. WEB后台管理:IP登录失败次数限制和用户登录失败次数,添加IP黑白名单，允许文件的操作类型开关，用户上传文件已用户分类
    3. 在 separate_path 函数中，构造相对路径默认添加 / 是否确认需要，该作用是为兼容，但会影响一点点性能
    4. 添加许可、文件更新 接口未验证 IP 次数，该功能是否需要添加？
更新：
    1. 新增账号密码验证。TOKEN_KEY 密钥的获取方式，使用账号密码的验证返回，以缓存的形式存储
    2. 文件操作成功后，数据写入到MySQL中
    3. 客户端获取文件数据列表接口取消，文件是否存在改为使用数据库验证！
    4. 新增 文件的删、改、移进行处理（仅验证了增文件）
    5. P登录失败15次 或 用户登录失败5次 将被限制十分钟
    6. 为了客户端支持重新运行，添加客户端响应type修改，类型为2的就是需要重新请求，类型3为提示
    7. 为了防止客户端没有验证服务端是否存在文件，必须验证后返回许可，上传添加的时候需要带上该许可
    8. 根据用户名分类文件夹，基本逻辑和文件的添加文件已完善，暂未打算启用
转为exe程序：pyinstaller -F -n monitor_file_s -i peng.ico  monitor_file_s.py
"""


from os import path, makedirs, remove
from cryptography.fernet import Fernet
from threading import Thread
from base64 import b64decode
from json import load
import concurrent.futures
import mysql.connector
from flask import Flask, request, jsonify
import logging
from datetime import datetime, timedelta
from mysql.connector import Error
from contextlib import closing
from shutil import move,rmtree

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


# 解密，下一个版本可能移除，如果拿到客户端源码就可以分析出加密过程了，所以可能没必要使用且还浪费性能处理！
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
    user_token_key = run_cache_data['login_pass'][username].encode()
    decrypted_secret_key = Fernet(user_token_key).decrypt(authorization_header.encode()).decode('utf-8')
    if decrypted_secret_key == secret_key:
        return True
    else:
        return False


# 文件类型验证，暂时不考虑做
def check_file_type(file_path):
    """
    文件类型验证
    :param file_path: 文件名
    :return: bool 类型
    """
    # 这里改为数据库
    allowed_extensions = {'jpg', 'jpeg', 'png', 'pdf', 'xml'}
    extension = file_path.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        logging.error(f"文件 {file_path} 类型不被允许。")
        return {'type': 0, 'mes': f'文件类型 {extension} 不被允许。'}


# 文件分离
def separate_path(file_path, file_name, username=''):
    """
    文件分离，用于文件的操作
    :param file_path: 用户上传的相对路径
    :param file_name: 用户上传的文件名
    :param username: 用户上传的 用户名
    :return: (服务器绝对路径文件名, 服务器相对路径文件名, 服务器绝对路径)
    """
    try:
        if is_user_path:
            user_path = username
        else:
            user_path = ''
        file_absolute_path = path.join(server_savefile, user_path, file_path.strip('/'), file_name).replace("\\", "/")
        # 构造路径是否需要添加 / 以满足兼容？
        file_relative_path = ("/" + path.join(user_path, file_path.strip('/'), file_name)).replace("\\", "/")
        absolute_path = path.join(server_savefile, user_path, file_path.strip('/')).replace("\\", "/")
        return file_absolute_path, file_relative_path, absolute_path
    except Exception as e:
        # 这里出现错误应该是用户名存在问题，如含特殊符号，在不同系统中有些允许
        logging.debug(f'文件分离错误：{e}')
        return False, False, False


# 添加保存数据文件
def save_data(file_absolute_path, file_relative_path, file_data):
    """
    添加保存数据文件
    :param file_absolute_path: 文件名的绝对路径
    :param file_relative_path: 文件名的相对对路径
    :param file_data: 二进制文件数据
    :return: {'type': 0, 'message': f'文件:{file_absolute_path} 保存完成！'}
    """
    try:
        # 保存文件到指定路径
        with open(file_absolute_path, 'wb') as f:
            f.write(file_data)
        # 验证文件是否成功保存
        if path.exists(file_absolute_path):
            logging.info(f"文件上传：{file_absolute_path} 上传成功！")
            # 添加成功数据
            add_file_sql = "INSERT INTO file_path (path) VALUES (%s)"
            execute_sql(add_file_sql, (file_relative_path,))
            logging.info(f'文件:{file_absolute_path} 保存完成！')
            return {'type': 0, 'message': f'文件:{file_absolute_path} 保存完成！'}
        else:
            logging.error(f"文件:{file_absolute_path} 保存失败，文件不存在。")
            return {'type': 1, 'error': '文件保存失败，文件不存在。'}

    except Exception as e:
        logging.error(f"无法保存文件:{file_absolute_path}: {e}")
        return {'type': 1, 'error': str(e)}


# 修改文件
def alter_data(file_absolute_path, file_data):
    try:
        with open(file_absolute_path, 'wb') as f:
            f.write(file_data)
        # 验证文件是否成功保存
        if path.exists(file_absolute_path):
            logging.info(f"文件修改：{file_absolute_path} 修改成功！")
            return {'type': 0, 'message': f'文件:{file_absolute_path} 修改完成！'}
        else:
            logging.error(f"文件:{file_absolute_path} 修改失败，文件不存在。")
            return {'type': 1, 'error': '文件修改失败，文件不存在。'}

    except Exception as e:
        logging.error(f"无法修改文件:{file_absolute_path}: {e}")
        return {'type': 1, 'mes': str(e)}


# 移动文件
def move_data(file_absolute_path, former_file_absolute_path, file_relative_path, former):
    """
    移动文件
    :param file_absolute_path: 新 文件绝对路径
    :param former_file_absolute_path: 旧 文件绝对路径
    :param file_relative_path: 新 文件相对路径
    :param former: 旧文件相对路径
    :return: 布尔值，指示移动是否成功
    """
    try:
        move(former_file_absolute_path, file_absolute_path)
        logging.info(f'{file_relative_path} 文件移动成功')
        # 添加成功数据
        sql = "UPDATE file_path SET path=%s where path=%s"
        execute_sql(sql, (file_relative_path,former,))
        return True
    except Exception as e:
        print(f"文件移动失败！: {e}")
        return False


# 删除文件
def del_data(file_absolute_path, file_relative_path):
    """
    删除文件或文件夹
    :param file_absolute_path: 文件绝对路径
    :param file_relative_path: 文件相对路径
    :return: 布尔值，指示删除是否成功
    """
    try:
        if path.isfile(file_absolute_path):  # 文件
            remove(file_absolute_path)
        elif path.isdir(file_absolute_path):  # 文件夹
            rmtree(file_absolute_path)
        else:
            print(f"{path} 不是有效文件或文件夹")
            return False
        sql = "DELETE FROM file_path WHERE path=%s "
        execute_sql(sql, (file_relative_path,))
        return True
    except OSError as e:
        print(f"Error while deleting {path}: {e}")
        return False


# 创建数据库连接
def create_db_connection():
    return mysql.connector.connect(**db_config)


def execute_sql(sql, params=None):
    """
    通用SQL执行
    :param sql: SQL 语句模板，可以包含占位符 %s
    :param params: 参数元组，用于填充 SQL 语句中的占位符
    :return: 布尔值，指示 SQL 执行是否成功
    """
    try:
        conn = create_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"执行SQL时出错: {e}")
        return False
    finally:
        if conn.is_connected():
            conn.close()


# 文件查询
def check_file_exists(file_path):
    try:
        conn = create_db_connection()
        with closing(conn.cursor()) as cursor:
            query = "SELECT EXISTS(SELECT 1 FROM file_path WHERE path = %s)"
            cursor.execute(query, (file_path,))
            result = cursor.fetchone()[0]
            return bool(result)
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")

    finally:
        if conn.is_connected():
            conn.close()


# 验证用户登录
def check_user(user, password):
    """
    用户登录验证
    :param user: 账号
    :param password: 密码
    :return: 布尔类型
    """
    try:
        conn = create_db_connection()
        with closing(conn.cursor()) as cursor:
            query = "SELECT user, password FROM username WHERE user = %s AND password = %s"
            cursor.execute(query, (user, password))
            result = cursor.fetchone()
            return result
    except Error as e:
        print("连接MySQL时出错:", e)
    finally:
        if conn.is_connected():
            conn.close()


def check_login_limit(client_ip, user):
    """
    检查登录是否被限制
    :param client_ip: IP地址
    :param user: 账号
    :return: 通过为 False
    """
    try:
        # 验证IP次数
        if client_ip in run_cache_data['login_limit_ip']:
            ip_data = run_cache_data['login_limit_ip'][client_ip]
            if ip_data.get('is_locked', False):
                last_attempt_time = ip_data['last_attempt_time']
                previous_time = datetime.strptime(last_attempt_time, '%Y-%m-%d %H:%M:%S')
                current_time = datetime.now()
                time_difference = current_time - previous_time
                # 检查是否超过2分钟
                if time_difference < timedelta(minutes=10):
                    return jsonify({"type": 2, "error": f"IP：{client_ip} 被锁定，请稍后再访问！上次访问时间：{last_attempt_time}"}), 400
                else:
                    ip_data['count'] = 0
                    ip_data['is_locked'] = False
        # 验证用户次数
        if user in run_cache_data['login_limit_user']:
            user_data = run_cache_data['login_limit_user'][user]
            if user_data.get('is_locked', False):
                last_attempt_time = user_data['last_attempt_time']
                previous_time = datetime.strptime(last_attempt_time, '%Y-%m-%d %H:%M:%S')
                current_time = datetime.now()
                time_difference = current_time - previous_time
                # 检查是否超过2分钟
                if time_difference < timedelta(minutes=10):
                    return jsonify({"type": 2, "error": f"用户：{user} 被锁定，请稍后再访问！上次访问时间：{last_attempt_time}"}), 400
                else:
                    user_data['count'] = 0
                    user_data['is_locked'] = False

        return False
    except Exception as e:
        logging.error(f'Error in check_login_limit: {e}')
        return jsonify({"type": 1, "error": "未知错误！"}), 400


def update_login_limit(client_ip, user):
    """
    更新登录限制计数
    :param client_ip: IP地址
    :param user: 账号
    """
    try:
        # 更新IP登录限制
        if client_ip in run_cache_data['login_limit_ip']:
            ip_data = run_cache_data['login_limit_ip'][client_ip]
            ip_data['count'] += 1
            if ip_data['count'] >= 15:
                ip_data['is_locked'] = True
                ip_data['last_attempt_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            run_cache_data['login_limit_ip'][client_ip] = {'count': 1, 'is_locked': False, 'last_attempt_time': ""}

        # 更新用户登录限制
        if user in run_cache_data['login_limit_user']:
            user_data = run_cache_data['login_limit_user'][user]
            user_data['count'] += 1
            if user_data['count'] >= 5:
                user_data['is_locked'] = True
                user_data['last_attempt_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            run_cache_data['login_limit_user'][user] = {'count': 1, 'is_locked': False, 'last_attempt_time': ""}

    except Exception as e:
        print(e)


# 触发上传处理
@app.route('/upload', methods=['POST'])
def upload_file():
    client_ip = request.remote_addr    # 记录IP地址
    try:
        token = request.form.get('token', False)  # 用户登录凭证
        token_key = request.form.get('token_key', False)  # 文件加密凭证
        file_name = request.form.get('filename', False)  # 文件名
        username = request.form.get('username', False)   # 用户名
        file_path = request.form.get('path', False)  # 相对路径
        file_type = request.form.get('type', False)  # 文件操作类型
        former = request.form.get('former', '')  # 旧文件的相对路径文件名
        add_token = request.form.get('add_token', '')    # 文件添加的许可凭证
        print(token,token_key,file_name, username, file_path,file_type,add_token)
        # 验证
        if token and token_key and file_name and username and file_path and file_type:
            if username not in run_cache_data['login_pass']:
                logging.error(f'文件上传_{username}:{client_ip}:验证失败，用户未登录！')
                return jsonify({'type': 2, 'error': f'用户：{username} 未登录！'}), 400
            if token != run_cache_data['login_pass'][username]:
                logging.info(f'文件上传_{username}:{client_ip}:验证失败，用户登录过期！')
                return jsonify({'type': 2, 'error': f'用户：{username} 登录过期！'}), 400
            if not decrypt(token_key, username, file_name):
                logging.error(f'文件上传_{username}:{client_ip}:验证失败，token_key不匹配！')
                return jsonify({'type': 1, 'error': 'token不匹配！'}), 400
        else:
            logging.info(f'文件上传_{username}:{client_ip}:验证失败，提交的数据不完整！')
            return jsonify({'type': 1, 'error': '提交的数据不完整！'}), 400

        # 绝对路径文件名, 相对路径文件名, 绝对路径文件夹
        file_absolute_path, file_relative_path, absolute_path = separate_path(file_path, file_name, username)

        # 添加文件操作记录SQL
        file_log_sql = """
                        INSERT INTO file_path_info (user, path, former_path, type, status, ip, info)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        # 文件操作类型
        if file_type == 'add':  # 添加
            # 验证文件的许可凭证验证
            if file_relative_path in run_cache_data['add_pass'][username]:
                if add_token != run_cache_data['add_pass'][username][file_relative_path]:
                    return jsonify({'type': 1, 'error': '该文件的add_token 没有经过验证！'}), 400
            else:
                return jsonify({'type': 1, 'error': f'{file_relative_path} 该文件没有经过验证！'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'type': 1, 'error': '上传的文件为空！'}), 400
            # 文件类型验证，验证源数据的文件后缀，暂时不考虑做
            # if check_file_type(file.filename):
            #     pass
            # 创建文件夹
            if not path.exists(absolute_path):
                makedirs(absolute_path, exist_ok=True)
            # 读取文件内容到内存中
            file_data = file.read()
            thread = Thread(target=save_data, args=(file_absolute_path, file_relative_path, file_data))
            thread.start()
            params = (username, file_relative_path, former, '添加', '成功', client_ip, '')
            execute_sql(file_log_sql, params)
            del run_cache_data['add_pass'][username][file_relative_path]   # 删除文件缓存凭证
            return jsonify({'type': 0, 'message': f'文件上传完成，等待服务器处理！ '}), 200

        elif file_type == 'alter':  # 修改
            file = request.files['file']
            if file.filename == '':
                return jsonify({'type': 1, 'error': '上传的文件为空！'}), 400
            # 读取文件内容到内存中
            file_data = file.read()
            if alter_data(file_absolute_path, file_data):
                params = (username, file_relative_path, former, '修改', '成功', client_ip, '')
                execute_sql(file_log_sql, params)
                return jsonify({'type': 0, 'message': f'文件修改完成，等待服务器处理！ '}), 200
            else:
                params = (username, file_relative_path, former, '修改', '失败', client_ip,'修改失败原因：待编写！')
                execute_sql(file_log_sql, params)
                return jsonify({'type': 1, 'message': f'文件修改失败，败原因：待编写！'}), 400

        elif file_type == 'move':  # 移动
            former_file_absolute_path = separate_path(former, file_name, username)[0]
            if move_data(file_absolute_path, former_file_absolute_path, file_relative_path, former):
                params = (username, file_relative_path, former, '移动', '成功', client_ip, '')
                execute_sql(file_log_sql, params)
                return jsonify({'type': 0, 'message': f'文件移动完成，等待服务器处理！ '}), 200
            else:
                params = (username, file_relative_path, former, '移动', '失败', client_ip, '移动失败原因：待编写！')
                execute_sql(file_log_sql, params)
                return jsonify({'type': 1, 'message': f'文件移动失败，败原因：待编写！'}), 400

        elif file_type == 'del':  # 删除
            if del_data(file_absolute_path, file_relative_path):
                params = (username, file_relative_path, former, '删除', '成功', client_ip, '')
                execute_sql(file_log_sql, params)
                return jsonify({'type': 0, 'message': f'文件删除完成，等待服务器处理！ '}), 200
            else:
                params = (username, file_relative_path, former, '删除', '失败', client_ip, '删除失败原因：待编写！')
                execute_sql(file_log_sql, params)
                return jsonify({'type': 1, 'message': f'文件删除失败，败原因：待编写！'}), 400
        else:
            return jsonify({'type': 1, 'error': '文件操作类型不支持！'}), 400

    except Exception as e:
        logging.error(f'数据上传：出错！！！ \n {e}')
        return jsonify({'type': 1,'error': f'请求错误！'}), 400


# 用户登录管理
@app.route('/login', methods=['POST'])
def login():
    client_ip = request.remote_addr
    try:
        if not request.form.get('username', False) or not request.form.get('password', False):
            logging.error(f'用户登录:{client_ip}:验证失败！ 没有提供账号或密码！')
            return jsonify({"type": 1, "error": "请提供账号和密码！"}), 400

        user, password = request.form['username'], request.form['password']
        # 检查是否被限制
        check_login = check_login_limit(client_ip, user)
        if check_login:
            return check_login

        # 验证用户
        user_data = check_user(user, password)
        if user_data:
            token_key = Fernet.generate_key().decode()
            logging.info(f'用户：{user} ，IP：{client_ip}，登录成功！')
            if user in run_cache_data['login_pass']:
                run_cache_data['login_pass'][user] = token_key  # 添加用户缓存凭证
            else:
                run_cache_data['login_pass'] = {user:token_key}
            run_cache_data['login_limit_ip'][client_ip] = {}  # 重置登录限制
            run_cache_data['login_limit_user'][user] = {}  # 重置登录限制
            return jsonify({"type": 0, "token": token_key}), 200
        else:
            update_login_limit(client_ip, user)
            return jsonify({"type": 1, "error": "账号或密码不正确！"}), 400
    except Exception as e:
        logging.error(f'用户登录:{client_ip}:验证失败！\n {e}')
        return jsonify({"type": 1, "error": "未知错误！"}), 400


# 检查文件是否存在
@app.route('/check', methods=['POST'])
def check_file():
    try:
        token = request.form.get('token', False)
        username = request.form.get('username', False)
        file_path = request.form.get('path', False)  # 相对路径文件名
        file_name = request.form.get('filename', False)  # 文件名
        if token and username in run_cache_data['login_pass'] and file_path and file_name:
            if token == run_cache_data['login_pass'][username]:
                file_path_name = separate_path(file_path, file_name, username)[1]
                if file_path_name:
                    if check_file_exists(file_path_name):
                        # logging.info(f"添加文件验证：{file_path_name} 文件存在")  减少日志量
                        return jsonify({'type': 0, 'message': f'{file_path_name} 文件存在！'}), 400
                    else:
                        add_token = Fernet.generate_key().decode()
                        if username in run_cache_data['add_pass']:
                            run_cache_data['add_pass'][username] = {file_path_name: add_token}
                        else:
                            run_cache_data['add_pass'] = {username: {file_path_name: add_token}}
                        logging.info(f"添加文件验证：{file_path_name} 文件不存在")
                        return jsonify({'type': 0, 'message': f'{file_path_name} 不文件不存在！', "add_token": add_token}), 200
            else:
                return jsonify({'type': 2, 'error': f'用户：{username} 登录过期！'}), 400
        else:
            return jsonify({'type': 1, 'error': f'未登录或没有文件名'}), 400
    except Exception as e:
        logging.error(f'文件检查：出错！！！ \n {e}')
        return jsonify({'type': 1, 'error': f'请求错误！'}), 400


# 检查配置文件
server_config = './server_config.json'
if not path.exists(server_config):
    print(f'配置文件不存在！！！！！！！')
    exit()

config_data = load_json_data(server_config)
if not config_data:
    print(f'配置文件有问题，请检查！')
    exit()

# 数据文件 配置 为了兼容之前的版本暂时仅新增
server_logs_filepath = config_data.get('server_logs_filepath', 'log')
server_savefile = config_data.get('server_save_filepath', './').replace('\\', '/')
server_host = config_data.get('server_host', '0.0.0.0')
server_port = config_data.get('server_port', 8080)
server_flask_debug = config_data.get('server_flask_debug', True)
server_thread = config_data.get('server_thread', 4)
# is_user_path = config_data.get('is_user_path', False)
is_user_path = False

# 数据库连接配置
db_config = {
    'host': config_data.get('db_host', '127.0.0.1'),
    'port': config_data.get('db_port', '3306'),
    'user': config_data.get('db_user', 'root'),
    'password': config_data.get('db_password', 'admin'),
    'database': config_data.get('db_database', 'mysql')
}

# 创建文件夹
makedirs(server_logs_filepath, exist_ok=True)
makedirs(server_savefile, exist_ok=True)

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

# 创建线程池
executor = concurrent.futures.ThreadPoolExecutor(max_workers=server_thread)

# 用户数据缓存，为了后期的后台开发，需要改为数据库的方式
run_cache_data = {
    "login_limit_ip": {
        "127.0.0.1": {
            "count": 1,
            "is_locked":False,
            "last_attempt_time":''
        }
    },
    "login_limit_user": {
        "admin": {
            "count": 1,
            "is_locked":False,
            "last_attempt_time":''
        }
    },
    "login_pass":{
        # "admin": "aaaaaaaaaaaaaaaaaaaa",
    },
    "add_pass": {
        # "admin":{'/1.txt':"AAAAAAAAAAAAAAAAA"}
    }
}

if __name__ == '__main__':
    app.run(host=server_host, port=server_port, debug=server_flask_debug)
