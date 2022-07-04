# coding:utf-8
import requests
import random
from xmltodict import parse
import os

'''
## 作者：玖伴一鹏
## 时间：2022.7.4
## 待完善
# 网址推送成功信息返回值的判断，以及推送网址失败的地址添加
# 程序仅能推送一次全部，如果不满足可以推送全部直接推送剩下的，不会继续推送剩下来的api接口次数
# 没有启用多线程，没有适配多方面的sitemap地址数据问题
# 当拿到url地址异常，没有做处理，每次运行总会遇到

## 待优化
# 程序在推送之前总是要判断地址长度是否符合，应该遍历文本文件保证不存在
# 存在很大的性能浪费问题

以上问题之后应该不会去改进，有时间可能会再做吧
'''

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


#  sitemap获取url地址
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
        json = {'siteUrl': name, 'urlList': url}
        # 必应的修改了，之前的没有注意，而且他的返回值为空
        print(requests.post(api, headers=headers, json=json, timeout=10))
        return {"msg": True}
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


# 谷歌的推送API(已经取消了，国内服务器没办法访问，只能自己改为xml提交)
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


# 运行需要参数
def run_info(url,api_run):
    try:
        # 判断文件是否存在
        if os.path.exists('txt_url.txt'):
            print("url文件存在...")
        else:
            print("txt_url.txt文件不存在，创建文件并爬取地址")
            url_txt = get_url(url).get("data").replace('\r\n', '\n')
            with open('txt_url.txt', 'w') as f:
                f.write(url_txt)
        if os.path.exists('txt_run.txt'):
            print("运行次数文件存在...")
        else:
            print("txt_run.txt文件不存在，创建文件")
            with open('txt_run.txt', 'w') as f:
                f.write('baidu:0\nbing:0\nsm:0')

        # 读取运行次数，百度到必应到神马，总是读取最后三行
        with open('txt_run.txt', 'r') as f:
            read_run = f.read().split('\n')[-3:]  # 读取倒数第三行到最后面的
            # 上次运行次数
            baidu_sum_run = eval(read_run[0].split(':')[1])
            bing_sum_run = eval(read_run[1].split(':')[1])
            sm_sum_run = eval(read_run[2].split(':')[1])
        # 拿到需要推送的url
        with open('txt_url.txt', 'r') as f:
            read_url = f.read().split('\n')  # url数据列表
            baidu_run_url = read_url[baidu_sum_run:]
            sm_run_url = read_url[sm_sum_run:]
            bing_run_url = read_url[bing_sum_run:]

            # 必应以列表的形式推送
            #bing_urllist = []
            if len(bing_run_url) > bing_api_run:
                # 之前以为必应一次可以推送一百个地址，仅占用一次api接口机会，结果还是仅可以推送100url地址
                # sum = 0
                # for i in range(1, len(bing_run_url) // bing_api_run + 2):
                #     bing_urllist.append(bing_run_url[sum * bing_api_run:i * bing_api_run])
                #     sum += 1
                bing_urllist = bing_run_url[baidu_api_run:baidu_api_run + api_run]
            else:
                bing_urllist = [bing_run_url]
        return {'baidu_sum_run': baidu_sum_run, 'bing_sum_run': bing_sum_run, 'sm_sum_run': sm_sum_run,
                'baidu_run_url': baidu_run_url, 'bing_run_url': bing_urllist, 'sm_run_url': sm_run_url,
                "msg": True}
    except Exception as s:
        print(s)
        return {"msg": False}


# 通用写入函数
def file_write(txt):
    with open('txt_run.txt', 'a') as f:
        f.write('\n{}'.format(txt))


# 修改部分
sitemap_url = "https://xs.jiubanyipeng.com/runtime/repaste/sitemap.txt"  # sitemap地址，我的是一条多个，就不做适配多条了, 如果你的有url地址的文本文件，直接命名为txt_url就可以了
name = "https://xs.jiubanyipeng.com/"  # 自己主页，必应需要
bing_api = "https://ssl.bing.com/webmaster/api.svc/pox/SubmitUrlBatch?apikey=你的"  # 必应AIP
baidu_api = "http://data.zz.baidu.com/urls?site=你的&token=你的"  # 百度AIP
sm_api = "https://data.zhanzhang.sm.cn/push?site=xs.jiubanyipeng.com&user_name=你的&resource_name=mip_add&token=你的"  # 神马API
bing_api_run, baidu_api_run, sm_api_run = 100, 3000, 10000  # 默认可推送推送次数，如果你的比这个多自己改
info = run_info(sitemap_url, bing_api_run)     # 运行数据信息,不用修改


# 运行百度，不满默认api运行次数直接运行后面剩余的次数，时间再改多线程
if len(info.get('baidu_run_url')) // baidu_api_run >= 1:
    baidu_urllist = info.get('baidu_run_url')
    sum_pass = 0
    for i in range(baidu_api_run):
        # 正常的地址长度至少在10个字符长度，但这里会影响速度
        if len(baidu_urllist[i]) < 7:
            continue
        print('百度推送，url地址：{}，当前推送数：{}'.format(baidu_urllist[i], sum_pass + 1))
        run_pass = baidu_push_urls(baidu_urllist[i],baidu_api)
        # 这里应该判断推送的返回值是否正确，做一个错误的url返回，感觉没有必要
        if run_pass.get('msg'):
            print(run_pass.get('data'))
            sum_pass += 1
    file_write('baidu:{}'.format(info.get('baidu_sum_run') + sum_pass))
else:
    sum_pass = 0
    for url in info.get('baidu_run_url'):
        if len(url) < 7:
            continue
        print('百度推送，url地址：{}，当前推送数：{}'.format(url, sum_pass + 1))
        run_pass = baidu_push_urls(url, baidu_api)
        # 这里应该做一个错误的url返回，感觉没有必要
        if run_pass.get('msg'):
            print(run_pass.get('data'))
            sum_pass += 1
    file_write('baidu:{}'.format(0))


# 运行必应,必应由于以列表的形式，一次就是满一百个地址
if len(info.get('bing_run_url')) == 100:
    print('必应推送，url地址长度：{}，当前从：{}开始推送'.format(len(info.get('bing_run_url')), info.get('bing_sum_run')))
    run_pass = bing_push_urls(name, info.get('bing_run_url'), bing_api)
    file_write('bing:{}'.format(info.get('bing_sum_run') + bing_api_run))
else:
    print('必应推送，url地址长度：{}，当前从：{}开始推送'.format(len(info.get('bing_run_url')), info.get('bing_sum_run')))
    run_pass = bing_push_urls(name, info.get('bing_run_url'), bing_api)
    file_write('bing:{}'.format(0))


# 运行神马
if len(info.get('sm_run_url')) // sm_api_run >= 1:
    sm_urllist = info.get('sm_run_url')
    sum_pass = 0
    for i in range(sm_api_run):
        if len(sm_urllist[i]) < 7:
            continue
        print('神马推送，url地址：{}，当前推送数：{}'.format(sm_urllist[i], sum_pass + 1))
        run_pass = sm_push_urls(sm_urllist[i], sm_api)
        if run_pass.get('msg'):
            print(run_pass.get('data'))
            sum_pass += 1
    file_write('sm:{}'.format(info.get('sm_sum_run')+ sum_pass))
else:
    sum_pass = 0
    for url in info.get('sm_run_url'):
        if len(url) < 7:
            continue
        print('神马推送，url地址：{}，当前推送数：{}'.format(url, sum_pass + 1))
        run_pass = sm_push_urls(url, sm_api)
        if run_pass.get('msg'):
            print(run_pass.get('data'))
            sum_pass += 1
    file_write('sm:{}'.format(0))


