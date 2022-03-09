import requests
from xmltodict import parse

'''
## 版本：3.2
## 作者：玖伴一鹏
## 日期：2022-3-9
## 更新：添加了分类、插件内链、标签网址，压缩代码、以确定接口次数
## 说明：我的图片网址有两个字典，所以要额外重新遍历
## 备注：两个插件生成的地图
'''

url = 'https://www.jiubanyipeng.ltd/'
url_list = [url+'sitemap-1.xml',  url+'surl-sitemap.xml', url+'category-sitemap.xml', url+'post_tag-sitemap.xml']
url_image = url+'image-sitemap-1.xml'    # 图片网址

# 遍历所有地址存到这里
url_lists = []
# aip运行次数
run = 0

# 文章 插件内链 插件内链 分类  标签
for i in url_list:
    get_url = requests.post(i).text
    date_url = parse(get_url)
    box_url = date_url.get('urlset', {})  # 获取最外面的一层，思路要根据字典的读取来
    context_url = box_url.get('url', {})  # 获取到多个列表
    for i in context_url:
        url = i.get('loc')  # 这里是标签，标签有值则@ ，获取文本用
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

print(url_lists)
# 必应的推送API
def bing_push_urls(urls):
    headers = {'Host': 'ssl.bing.com', 'Content-Type': 'application/json; charset=utf-8'}
    api = 'https://ssl.bing.com/webmaster/api.svc/json/SubmitUrl?apikey=自己的'
    json = {
        'siteUrl': 'https://jiubanyipeng.ltd',
        'url': urls
    }
    response = requests.post(api, headers=headers, json=json, timeout=10).text
    return response


# 百度的推送API
def baidu_push_urls(urls):
    headers = {'User-Agent': 'curl/7.12.1', 'Host': 'data.zz.baidu.com', 'Content-Type': 'text/plain', 'Content-Length': '83'}
    api = 'http://data.zz.baidu.com/urls?site=自己的&token=自己的'
    response = requests.post(api, headers=headers, data=urls, timeout=10).text
    return response


# 谷歌的推送API(已经取消了，xml提交)
# def google_push_urls(urls):


# 神马的推送API
def sm_push_urls(urls):
    headers = {'User-Agent': 'curl/7.12.1', 'Host': 'data.zhanzhang.sm.cn', 'Content-Type': 'text/plain', 'Content-Length': '83'}
    api = 'https://data.zhanzhang.sm.cn/push?site=自己的&user_name=自己的&resource_name=mip_add&token=自己的'
    response = requests.post(api, headers=headers, data=urls, timeout=10).text
    return response


# 后期数据超过100条，先把数据存到第一个文件中，判断文件数据大小...
# if len(url_lists) > 100:

##  网址的总长度确定遍历次数，大于100另外算还没考虑
bing_run = 100 // len(url_lists) + 1
baidu_run = 3000 // len(url_lists) + 1
sm_run = 10000 // len(url_lists) + 1

# 运行必应推送
for i in range(bing_run):
    for i in range(len(url_lists)):
        run += 1
        bing = bing_push_urls(url_lists[i])
        print("推送网址： " + url_lists[i], "\n", bing)
        if run == 100:
            print("运行次数已到100")
            break

# 运行百度推送
for i in range(baidu_run):
    for i in range(len(url_lists)):
        run += 1
        baidu = baidu_push_urls(url_lists[i])
        print("推送网址： " + url_lists[i], "\n", baidu)
        if run == 3000:
            print("运行次数已到3000")
            break

# 运行神马推送
for i in range(sm_run):
    for i in range(len(url_lists)):
        run += 1
        sm = sm_push_urls(url_lists[i])
        print("推送网址： " + url_lists[i], "\n", sm)
        if run == 10000:
            print("运行次数已到10000")
            break








