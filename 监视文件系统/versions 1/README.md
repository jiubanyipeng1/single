<h1>文件监视上传系统</h1>
1. 主要功能：客户端新增文件（其他操作未开发），将文件上传到服务端。 <br>
2. 原理：客户端通过监视本地某个文件夹，当文件夹里面有文件的变动时（目前仅监视文件的创建），将文件相关的信息传输到服务器。<br>

<h1>注意</h1>
该版本不再维护，仅适合轻量化，也不兼容之后的版本！
<h1>使用</h1>
1. 由于比较匆忙，环境自己看需要引入哪些库。 先在配置文件相关配置，后面运行server，再运行client<br>
2. 客户端配置文件：client_config.json <br>
3. 服务端配置文件:server_config.json <br>
4. 如果你不懂开发环境安装，直接下载集成环境（<a href="https://github.com/jiubanyipeng1/single/releases/tag/1.1" target="_blank">下载地址</a> ），里面有64位系统运行程序，其他版本暂时不考虑提供。 <br>
5. 为了安全，token秘钥一般是自己生成，由于目前还没有配置相关的账号验证，最好是自己随机生成秘钥，参考：
<pre>
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode('utf-8'))
</pre>
<h1> 配置文件参考说明 </h1>
<table>
    <caption><h5>server_config文件说明：</h5></caption>
    <tr align="center">
        <th>键名</th>
        <th>参考值</th>
        <th>说明</th>
    </tr>
    <tr align="center">
        <td>token_key</td>
        <td>"N5ACrj3J5nDVEeFBuLATrfPEXR-Rt0pzuZN3LaA8mzI="</td>
        <td>用于对称加密的秘钥。注意：客户端秘钥和服务端秘钥要相同</td>
    </tr>
    <tr align="center">
        <td>data_filepath</td>
        <td>"filesdata.txt"</td>
        <td>记录服务端保存文件成功的数据，可定义在前面添加文件路径和自定义文件名</td>
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
</table>

<table>
    <caption><h5>client_config说明</h5></caption>
    <tr align="center">
        <th>键名</th>
        <th>参考值</th>
        <th>说明</th>
    </tr>
    <tr align="center">
        <td>token_key</td>
        <td>"N5ACrj3J5nDVEeFBuLATrfPEXR-Rt0pzuZN3LaA8mzI="</td>
        <td>用于对称加密的秘钥。注意：客户端秘钥和服务端秘钥要相同</td>
    </tr>
    <tr align="center">
        <td>username</td>
        <td>"admin"</td>
        <td>进行验证的账号用户</td>
    </tr>
    <tr align="center">
        <td>passwd</td>
        <td>"admin"</td>
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
        <td>client_logs_filepath</td>
        <td>"logs"</td>
        <td>客户端运行的的日志文件夹地址</td>
    </tr>
    </table>
    
