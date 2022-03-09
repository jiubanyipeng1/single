import requests
from xmltodict import parse

'''
## 版本：2.1
## 作者：玖伴一鹏
## 日期：2022-3-8
## 更新：添加了图片地址推送，注意图片路径占时不能是中文
'''

# 要推送网址
url_list = 'https://www.jiubanyipeng.ltd/sitemap-1.xml'  # 网址地图
url_image = 'https://www.jiubanyipeng.ltd/image-sitemap-1.xml'  # 图片地图

url_lists = []  # 遍历的网站跟图片存到这里

# 获取网站列表
get_url = requests.post(url_list).text  # 获取到的是xml
date_url = parse(get_url)  # 转成字典
box_url = date_url.get('urlset', {})  # 获取最外面的一层，思路要根据字典的读取来
context_url = box_url.get('url', [])  # 获取到多个列表
for m in context_url:
    url = m.get('loc')  # 这里是标签，标签有值则@ ，获取文本用#
    url_lists.append(url)  # 追加到列表中

# 获取图片列表
get_image = requests.post(url_image).text
date_image = parse(get_image)
box_image = date_image.get('urlset', {})
context_image = box_image.get('url', {})  # 字典
for i in context_image:
    url = i.get('image:image', [])
    for i in range(1):
        url = url.get('image:loc', [])
        url_lists.append(url)



# 必应的推送API
def bing_push_urls(urls):
    headers = {'Host': 'ssl.bing.com', 'Content-Type': 'application/json; charset=utf-8', }
    api = 'https://ssl.bing.com/webmaster/api.svc/json/SubmitUrl?apikey=自己的'
    json = {
        'siteUrl': 'https://自己的',
        'url': urls,
    }
    response = requests.post(api, headers=headers, json=json, timeout=10).text
    return response


# 百度的推送API
def baidu_push_urls(urls):
    headers = {'User-Agent': 'curl/7.12.1', 'Host': 'data.zz.baidu.com', 'Content-Type': 'text/plain',
               'Content-Length': '83'}
    api = 'http://data.zz.baidu.com/urls?site=https://自己的&token=自己的'
    response = requests.post(api, headers=headers, data=urls, timeout=10).text
    return response


# 谷歌的推送API(已经取消了，xml提交)
# def google_push_urls(urls):


# 神马的推送API
def sm_push_urls(urls):
    headers = {'User-Agent': 'curl/7.12.1', 'Host': 'data.zhanzhang.sm.cn', 'Content-Type': 'text/plain',
               'Content-Length': '83'}
    api = 'https://data.zhanzhang.sm.cn/push?site=www.自己的&user_name=自己的&resource_name=mip_add&token=自己的'
    response = requests.post(api, headers=headers, data=urls, timeout=10).text
    return response


# 后期数据超过100条，先把数据存到第一个文件中，判断文件数据大小...
# if len(url_lists) > 100:

## 这里决定数据运行次数，根据api接口
bing_run = 100 // len(url_lists) + 1
baidu_run = 3000 // len(url_lists) + 1
sm_run = 10000 // len(url_lists) + 1

# 运行必应推送
for i in range(bing_run):
    for i in range(len(url_lists)):
        bing = bing_push_urls(url_lists[i])
        print("推送网址： " + url_lists[i], "\n", bing)

# 运行百度推送
for i in range(baidu_run):
    for i in range(len(url_lists)):
        baidu = baidu_push_urls(url_lists[i])
        print("推送网址： " + url_lists[i], "\n", baidu)

# 运行神马推送
for i in range(sm_run):
    for i in range(len(url_lists)):
        sm = sm_push_urls(url_lists[i])
        print("推送网址： " + url_lists[i], "\n", sm)








