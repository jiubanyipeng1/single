'''
### 定时脚本
### 其它脚本的使用别人的，源作者地址：https://github.com/wangquanfugui233/Bilibili_Python
### 第一次运行会自己生成 Bilibili_config.json 配置文件
### 配置文件说明：
# coin：投币， 做任务时投币的数量
# max_pageL: 扫描天选页数
# max_thread: 扫描线程数
# black_list:黑名单, 就是你不想关注的up主mid放在这里，一定要是英文逗号
# white_list:白名单, 就是你不想取关的，和中奖的up主mid会存在这里，一定要是英文逗号
# favorite:指定给up主投币，做日常任务时投币的任务
# follow_author：关注源作者的账号（源作者的账号好像被封了）。不想关注就写False
# 多账号格式：---》：{"Cookie": ""},{"Cookie": ""},{"Cookie": ""}..... 一定要是英文逗号
仅供个人学习，不得用于牟利，仅供学习参考
'''


import Bilibili_Config    # 运行前检查配置文件
from apscheduler.schedulers.blocking import BlockingScheduler  # 定时任务框架
import json
import sys

# 参加天选时刻
def Bilibili_CTime():
    import Bilibili_CTime


# 运行日常任务
def Bilibili_Dayly():
    import Bilibili_Daily


# 取消关注
def Bilibili_Unfollows():
    import Bilibili_Unfollows


# 中奖通知
def Bilibili_Prize():
    import Bilibili_Prize


# 运行
def func(tx_cron, rc_cron, qx_cron, zj_cron):
    scheduler = BlockingScheduler()
    try:
        scheduler.add_job(Bilibili_CTime, 'cron',  year='*', month='*', day=f'{tx_cron[2]}', hour=f'{tx_cron[1]}', minute=f'{tx_cron[0]}', id='run1', name='参加天选时刻', jitter=120)
        scheduler.add_job(Bilibili_Dayly, 'cron',  day=f'{rc_cron[2]}', hour=f'{rc_cron[1]}', minute=f'{rc_cron[0]}', id='run2', name='运行日常任务', jitter=120)
        scheduler.add_job(Bilibili_Unfollows, 'cron', day=f'{qx_cron[2]}', hour=f'{qx_cron[1]}', minute=f'{qx_cron[0]}', id='run3', name='运行取消关注任务', jitter=120)
        scheduler.add_job(Bilibili_Prize, 'cron',  day=f'{zj_cron[2]}', hour=f'{zj_cron[1]}', minute=f'{zj_cron[0]}', id='run4', name='中奖通知', jitter=120)
        scheduler.start()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    try:
        with open('Bilibili_config.json') as f:
            if len(json.loads(f.read())['Users'][0]['Cookie']) < 1:
                print('cookie为空或没有设置好，先设置好cookie！')
                sys.exit()
        # 下面的是cron 表达式，不懂的可以百度搜索 cron 在线生成器，可以有效帮助
        # 分 时 日  ，为了兼容，必须三个数据，且空格分开，不要多个空格
        tx_cron = '22 17-20 *'    # 天选时刻，每天运行三次，分别12点12分、13点12分、14点12分开始运行，一天最多只能运行四次，超过cookie过期
        rc_cron = '15 20 *'    # 日常任务，每天运行1次，每天的15点12分开始运行
        qx_cron = '25 20 *'    # 取消关注，每天运行1次，每天的15点25分开始运行
        zj_cron = '30 20 *'    # 中奖通知，每天运行1次，每天的15点30分开始运行

        if len(tx_cron.split(' ')) == 3 and len(rc_cron.split(' ')) == 3 and len(qx_cron.split(' ')) == 3 and len(
                zj_cron.split(' ')) == 3:
            func(tx_cron.split(' '), rc_cron.split(' '), qx_cron.split(' '), zj_cron.split(' '))
        else:
            print('你的cron值错了,请检查！')

    except Exception as e:
        print('cookie为空或没有设置好，先设置好cookie！')


