# -*- coding:utf-8 -*-
# WordPress转成静态html,在命令行下任意添加一个参数便重新缓存
import requests
from xmltodict import parse
import sys


# 获取url列表
def get_url(url_list):
    try:
        url_lists = []  # 遍历所有地址存到这里
        for i in url_list:
            date_url = parse(requests.post(i).text)
            for url in date_url.get('urlset', {}).get('url', {}):
                url_lists.append(url.get('loc',''))
        return url_lists
    except Exception as e:
        print('错误：',e)
        return []


def get_text(url,url_lists):
    with open('url.txt', 'r', encoding='utf-8') as f:
        in_url = f.read().split('\n')
    for i in url_lists:
        name = i.replace(url,'')
        if '/' in name:
            print('存在子分类，由于文件夹和文件不能同名，这里就不在做子分类的延续')
            continue
        # 已经缓存的文件就不再缓存
        if len(sys.argv) > 1:
            print(f'{name}重新缓存中...')
        else:
            if name in in_url:
                continue
        try:
            html = requests.post(i).text
            if name == '':
                name = 'index.html'
            with open(f'{name}','w',encoding='utf-8') as ff:
                ff.write(html)
            with open('url.txt', 'a', encoding='utf-8') as fff:
                fff.write(name + '\n')
        except Exception as e:
            print(e)


url = 'https://www.jiubanyipeng.com/'   # 这里是用来替换使用的，一定要完整的url地址且要加上 /
url_list = [url+'post-sitemap.xml',  url+'page-sitemap.xml', url+'category-sitemap.xml']  # 文章 插件内链 插件内链 分类  标签  等自己添加进来
get_text(url,get_url(url_list))
