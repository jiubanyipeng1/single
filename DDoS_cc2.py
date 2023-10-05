# -*- coding:utf-8 -*-
import asyncio
from aiohttp import ClientSession

tasks = []
url = "https://www.jiubanyipeng.com/1114.html"
async def hello(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            return response.status

def run():
    for i in range(50):
        task = asyncio.ensure_future(hello(url))
        tasks.append(task)
    result = loop.run_until_complete(asyncio.gather(*tasks))
    print(result)

if __name__ == '__main__':
    while True:
        loop = asyncio.get_event_loop()
        run()