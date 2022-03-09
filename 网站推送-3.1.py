import requests
from xmltodict import parse

'''
## 版本：3.1
## 作者：玖伴一鹏
## 日期：2022-3-9
## 更新：添加了分类、插件内链、标签网址
## 说明：前三个版本都是由Jetpack生成的XML站点地图，只有文章跟页面，没有作者和分类以及插件生成的内链
## 备注：所有的地址至少要有两个以上，不然遍历地址字典时get不到地址列表,没有添加作者网址，不能是网址中文，推送的api接口暂时不支持
'''

# 要推送网址
url_list = 'https://www.jiubanyipeng.ltd/sitemap-1.xml'  # 文章
url_image = 'https://www.jiubanyipeng.ltd/image-sitemap-1.xml'  # 图片
url_surl = 'https://www.jiubanyipeng.ltd/surl-sitemap.xml'  # 插件内链
url_category = 'https://www.jiubanyipeng.ltd/category-sitemap.xml'  # 分类
url_tag = 'https://www.jiubanyipeng.ltd/post_tag-sitemap.xml'  # 标签

# 遍历所有地址存到这里
url_lists = []

# 获取文章列表（包括页面）
get_url = requests.post(url_list).text  # 获取到的是xml
date_url = parse(get_url)  # 转成字典
box_url = date_url.get('urlset', {})  # 获取最外面的一层，思路要根据字典的读取来
context_url = box_url.get('url', {})  # 获取到多个列表
for m in context_url:
    url = m.get('loc')  # 这里是标签，标签有值则@ ，获取文本用
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

# 获取内链列表
get_surl = requests.post(url_surl).text
date_surl = parse(get_surl)
box_surl = date_surl.get('urlset', {})
context_surl = box_surl.get('url', {})
for i in context_surl:
    url = i.get('loc', [])
    url_lists.append(url)

# 获取分类列表
get_category = requests.post(url_category).text
date_category = parse(get_category)
box_category = date_category.get('urlset', {})
context_category = box_category.get('url', {})
for i in context_category:
    url = i.get('loc', [])
    url_lists.append(url)

# 获取标签
get_tag = requests.post(url_tag).text
date_tag = parse(get_tag)
box_tag = date_tag.get('urlset', {})
context_tag = box_tag.get('url', {})
for i in context_tag:
    url = i.get('loc', [])
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
    api = 'https://data.zhanzhang.sm.cn/push?site=自己的&user_name=自己的&resource_name=mip_add&token=自己的'
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








