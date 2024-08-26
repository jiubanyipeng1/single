<h1>文件监视上传系统</h1>
1. 主要功能：客户端新增文件（其他操作未开发），将文件上传到服务端。 <br>
2. 原理：客户端通过监视本地某个文件夹，当文件夹里面有文件的变动时（目前仅监视文件的创建），将文件相关的信息传输到服务器。<br>
<h1>声明：提供源码仅是为了个人的学习与研究，不得用于非法以及其他用途，造成一切后果自负！</h1>
<h1>使用</h1>
1. 由于比较匆忙，环境自己看需要引入哪些库。 先在配置文件相关配置，后面运行server，再运行client<br>
2. 客户端配置文件：client_config.json <br>
3. 服务端配置文件:server_config.json <br>
4. 基本表的数据结构sql：monitor_file_sql.sql <br>
5. 如果你不懂开发环境安装，直接下载集成环境（<a href="https://github.com/jiubanyipeng1/single/releases/tag/2.1" target="_blank">下载地址</a> ）<br>
<h1>更新说明：</h1>
2.1 
<h1> 配置文件参考说明 </h1>
<table>
    <caption><h5>server_config文件说明：</h5></caption>
    <tr align="center">
        <th>键名</th>
        <th>参考值</th>
        <th>说明</th>
    </tr>
    <tr align="center">
        <td>server_save_filepath</td>
        <td>"H:\\服务器文件"</td>
        <td>服务端保存文件的绝对路径地址。</td>
    </tr>
    <tr align="center">
        <td>server_logs_filepath</td>
        <td>"logs"</td>
        <td>运行日志文件夹地址，可自定义绝对路径</td>
    </tr>
    <tr align="center">
        <td>server_host</td>
        <td>"0.0.0.0"</td>
        <td>flask运行参数，运行的主机IP地址，参考是代表本机所有地址</td>
    </tr>
    <tr align="center">
        <td>server_port</td>
        <td>8080</td>
        <td>服务器运行的端口，注意：客户端配置url地址需要对应！</td>
    </tr>
    <tr align="center">
        <td>server_flask_debug</td>
        <td>true</td>
        <td>flask是否开启bug调试提示</td>
    </tr>
    <tr align="center">
        <td>server_thread</td>
        <td>4</td>
        <td>运行最大的线程</td>
    </tr>
    <tr align="center">
        <td>is_user_path</td>
        <td>false</td>
        <td>是否添加客户端上传的路径，以用户文件夹开始</td>
    </tr>
    <tr align="center">
        <td>db_host</td>
        <td>'127.0.0.1'</td>
        <td>数据库配置：数据库主机地址</td>
    </tr>
    <tr align="center">
        <td>db_port</td>
        <td>'3306'</td>
        <td>数据库配置：端口号</td>
    </tr>
    <tr align="center">
        <td>db_user</td>
        <td>'root'</td>
        <td>数据库配置：登录的用户名</td>
    </tr>
    <tr align="center">
        <td>db_password</td>
        <td>'123456'</td>
        <td>数据库配置：登录的密码</td>
    </tr>
    <tr align="center">
        <td>db_database</td>
        <td>'fileupload'</td>
        <td>数据库配置：默认选择的数据库</td>
    </tr>
</table>

<table>
    <caption><h5>client_config说明</h5></caption>
    <tr align="center">
        <th>键名</th>
        <th>参考值</th>
        <th>说明</th>
    </tr>
    <tr align="center">
        <td>username</td>
        <td>"admin"</td>
        <td>进行验证的账号用户</td>
    </tr>
    <tr align="center">
        <td>passwd</td>
        <td>"password"</td>
        <td>进行验证的账号用户密码</td>
    </tr>
    <tr align="center">
        <td>server_url</td>
        <td>"http://192.168.2.85:8080"</td>
        <td>服务器的完整URL地址，注意需要带上端口，后面也没有/</td>
    </tr>
    <tr align="center">
        <td>client_path</td>
        <td>"H:\客户端文件"</td>
        <td>客户端监听的文件夹地址</td>
    </tr>
    <tr align="center">
        <td>excluded_dirs</td>
        <td>["H:\\客户端文件\\排除文件夹"]</td>
        <td>客户端监听的文件夹地址排除，默认将日志添加</td>
    </tr>
    </table>
    
<h1> SQL文件参考 </h1>
注意：默认的SQL在username表插入一条数据，账号：admin，密码：password
<pre>
CREATE TABLE IF NOT EXISTS `file_path_info`  (
  `id` INT AUTO_INCREMENT PRIMARY KEY UNIQUE COMMENT '主键id',
  `user` VARCHAR(20) NOT NULL  COMMENT '用户',
  `path` VARCHAR(255) NOT NULL COMMENT '本次操作文件路径',
  `former_path` VARCHAR(255) DEFAULT NULL COMMENT '旧文件路径',
  `type` VARCHAR(10) NOT NULL COMMENT '类型',
  `status` VARCHAR(10) NOT NULL COMMENT '状态',
  `ip` VARCHAR(15) NOT NULL COMMENT 'IP地址',
  `info` VARCHAR(20) NULL DEFAULT '无' COMMENT '操作信息',
  `update` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='文件路径信息操作详情表';

CREATE TABLE `file_path`  (
  `path` varchar(255) NOT NULL UNIQUE PRIMARY KEY COMMENT '文件路径',
  `update` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='文件路径信息表';

CREATE TABLE `username`  (
  `user` varchar(20) NOT NULL PRIMARY KEY UNIQUE COMMENT '用户' ,
  `password` varchar(64) NOT NULL COMMENT '密码',
  `is_start` TINYINT(1) NOT NULL  DEFAULT 0 COMMENT '是否启用账号，0:代表启用 1:代表不启用',
  `username` varchar(20) NULL COMMENT '用户名称',
  `power` varchar(10) NULL COMMENT '用户权限（保留扩展使用）',
  `update` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='用户表';

CREATE TABLE `check_file_type`  (
  `id` INT AUTO_INCREMENT PRIMARY KEY UNIQUE COMMENT '主键id',
  `is_start` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否启用 0代表允许 1 代表不允',
  `file_type` varchar(15) NOT NULL UNIQUE COMMENT '文件类型',
  `file_type_descr` varchar(50) NULL COMMENT '文件类型备注',
  `update` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='允许的文件后缀';

CREATE TABLE `login_attempts` (
  `user` varchar(20) NOT NULL PRIMARY KEY UNIQUE COMMENT '用户',
  `attempts` TINYINT(3) NOT NULL DEFAULT 0  COMMENT '尝试次数',
  `last_attempt_time` DATETIME DEFAULT NULL  COMMENT '最后一次尝试时间',
  `permit_max` TINYINT(3) NOT NULL DEFAULT 5 COMMENT '允许最大尝试次数',
  `is_locked` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否锁定 0代表锁定 1 代表不锁定',
  `update` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='登录次数限制表' ;


CREATE TABLE `ip_whitelist` (
  `ip_address` VARCHAR(15) NOT NULL PRIMARY KEY COMMENT 'IP地址',
  `is_ip` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否启用 0代表白名单 1 代表黑名单',
  `update` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='IP黑白名单表';


INSERT INTO `username` (`user`, `password`, `username`, `power`)
VALUES ('admin', 'password', '管理员', 'admin');
</pre>
