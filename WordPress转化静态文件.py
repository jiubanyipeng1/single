# -*- coding:utf-8 -*-
# WordPress转成静态html,在命令行下任意添加一个参数便重新缓存
import requests
from xmltodict import parse
import sys,time,os


# 获取url列表，返回的是地址列表 ['https://www.abc.com/2.html','https://www.abc.com/3.html']
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
    if not os.path.exists('./url.txt'):
        with open('./url.txt', 'w') as f:
            print('url.txt 文件不存在 已创建文件')
    with open('./url.txt', 'r') as f1:
        in_url = f1.read().strip().split('\n')
        # 缓存操作
        if len(sys.argv) > 1:
            print('重新缓存中...')
            for s in in_url:
                if s == '':
                    s = 'index.html'
                print(f'删除： {s}')
                try:
                    os.remove(s)
                except Exception as e:
                    print(f'{s} 删除失败！')
            in_url = []
            with open('./url.txt', 'w', encoding='utf-8') as ff:
                pass
            print('清空缓存完成，正在重新获取')
        for i in url_lists:
            name = i.replace(url,'')
            if '/' in name:
                print('存在子分类，由于文件夹和文件不能同名，这里就不在做子分类的延续')
                continue
            # 已经缓存的文件就不再缓存
            if name in in_url:
                continue
            try:
                print(f'获取: {i}')
                time.sleep(1)  # 防止太快被服务器防火墙封禁
                html = requests.post(i).text
                if name == '':
                    name = 'index.html'
                with open(f'{name}','w',encoding='utf-8') as ff:
                    ff.write(html)
                with open('./url.txt', 'a', encoding='utf-8') as fff:
                    fff.write(name + '\n')
            except Exception as e:
                print(e)


url = 'https://www.jiubanyipeng.com/'   # 这里是用来替换使用的，一定要完整的url地址且要加上 /
url_list = [url+'post-sitemap.xml',  url+'page-sitemap.xml', url+'category-sitemap.xml']  # 网站地图，不一定兼容（本站文章 插件内链 分类  标签）
get_text(url,get_url(url_list))
