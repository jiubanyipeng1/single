<table>
    <caption><h5>web_config说明</h5></caption>
    <tr align="center">
        <th>键名</th>
        <th>参考值</th>
        <th>说明</th>
    </tr>
    <tr align="center">
        <td>port</td>
        <td>9999</td>
        <td>类型为：整型，web启动的端口。</td>
    </tr>
    <tr align="center">
        <td>path</td>
        <td>''</td>
        <td>类型为：字符，聊天地址。默认为空，直接访问，如果添加字符串在访问时需要加上对应的地址。</td>
    </tr>
    <tr align="center">
        <td>streaming</td>
        <td>false</td>
        <td>类型为：布尔，如果启用，GPT对接将以流式的方式返回，该功能未开发！</td>
    </tr>
  <tr align="center">
        <td>login</td>
        <td>false</td>
        <td>类型为：布尔，如果启用，聊天对话之前需要进行登录，该功能未开发！</td>
    </tr>
    <tr align="center">
        <td>user_data</td>
        <td>[{"暂未使用,后期保留扩展处理": "admin"},{"账号": "密码"}]</td>
        <td>类型为：列表，列表中的字典是登录的账号和密码，该功能未开发！</td>
    </tr>
</table>
