# coding:utf-8
import requests
import random
from xmltodict import parse


# User-Agent
user_agent = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32",
]


# URL访问通用函数
def get_url(url):
    try:
        header = {"User-Agent": random.choice(user_agent)}
        res = requests.get(url, headers=header, timeout=5).text
        return {'data': res, 'msg': True}
    except Exception as e:
        print(e)
        return {'msg': False}


# 获取url地址
def get_urllist(url):
    try:
        url_list = []
        sitemap_index = parse(get_url(url).get('data'))['sitemapindex']['sitemap']
        for push_url in [i['loc'] for i in sitemap_index]:
            url_list.append(push_url)
            url_sitemap_list = parse(get_url(push_url).get('data'))['urlset']['url']
            for i in url_sitemap_list:
                if type(i) == type('str'):
                    continue
                if len(i) == 2:
                    url_list.append(i['loc'])
                if len(i) == 3:
                    for s in i['image:image']:
                        url_list.append(s['image:loc'])
        return {"data": url_list, "msg": True}
    except Exception as s:
        print(s)
        return {"msg": False}


# 必应的推送API
def bing_push_urls(name, url, api):
    try:
        headers = {'Host': 'ssl.bing.com', 'Content-Type': 'application/json; charset=utf-8'}
        json = {'siteUrl': name, 'url': url}
        response = requests.post(api, headers=headers, json=json, timeout=10).text
        return {"data": response, "msg": True}
    except Exception as s:
        print(s)
        return {"msg": False}


# 百度的推送API
def baidu_push_urls(url, api):
    try:
        headers = {'User-Agent': 'curl/7.12.1', 'Host': 'data.zz.baidu.com', 'Content-Type': 'text/plain', 'Content-Length': '83'}
        response = requests.post(api, headers=headers, data=url, timeout=10).text
        return {"data": response, "msg": True}
    except Exception as s:
        print(s)
        return {"msg": False}


# 谷歌的推送API(已经取消了，xml提交)
# def google_push_urls(urls):


# 神马的推送API
def sm_push_urls(url, api):
    try:
        headers = {'User-Agent': 'curl/7.12.1', 'Host': 'data.zhanzhang.sm.cn', 'Content-Type': 'text/plain', 'Content-Length': '83'}
        response = requests.post(api, headers=headers, data=url, timeout=10).text
        return {"data": response, "msg": True}
    except Exception as s:
        print(s)
        return {"msg": False}

# 修改部分
sitemap_url = "https://www.jiubanyipeng.com/sitemap_index.xml"   # 我的事使用  Yoast SEO 生成，其他的没有做适配
name = "https://www.jiubanyipeng.com/"  # 自己主页，必应需要
bing_api = "https://ssl.bing.com/webmaster/api.svc/json/SubmitUrl?apikey=自己的"  # 必应AIP
baidu_api = "http://data.zz.baidu.com/urls?site=自己的&token=自己的"  # 百度AIP
sm_api = "https://data.zhanzhang.sm.cn/push?site=自己的&user_name=自己的&resource_name=mip_add&token=自己的"  # 神马API
push_url = get_urllist(sitemap_url)  # 如果不适配，这里修改成列表，如：push_url=['网址1','网址2']，如果你的很多可以放到文本里面自己通过读写操作，变成列表

# 运行
for i in range(len(push_url)):
    bing = bing_push_urls(name, push_url[i], bing_api)
    if bing.get("msg"):
        print(bing.get("data"))
    baidu = baidu_push_urls(push_url[i], baidu_api)
    if baidu.get("msg"):
        print(bing.get("data"))
    shenma = sm_push_urls(push_url[i], sm_api)
    if shenma.get("msg"):
        print(shenma.get("data"))
