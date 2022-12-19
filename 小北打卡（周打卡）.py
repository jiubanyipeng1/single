# -*- coding: utf-8 -*-
'''
### 该版本是一个星期仅运行一次
### 本次更新：优化了定时运行的算法，当星正确时，便默认先运行一次，之后的时间也会精准
### 时间的算法 单位根据小时，没有精确到分秒
### 2022.12.19  更新
'''

import base64, random, time, datetime
import requests


# 定义星期几运行  星期天到星期六：0-6
timeweek = '5'
# 定义当天的运行时间 24小时制（最早早上7点）
timeing = '7'
# 本来是想使用百度地图的接口，只几个人需要就算了
# 设置账号 密码 密码 经纬度 城市
array = [
    ["17677666666", "666666", "109.6200000000000,23.20000000000","中国-广西壮族自治区-花花市-花花区"],
    ["账号二", "密码二", "经度,维度","国-省-市-区（县）"],
    ["账号三", "密码三", "经度,维度","中国-广西壮族自治区-桂林市-永福县"],
    ["账号四", "密码四", "经度,维度","中国-广东省-佛山市-顺德区"],
    ["账号五", "密码五", "经度,维度","中国-广西壮族自治区-河池市-都安瑶族自治县"],
]
# API地址
BASE_URL = "https://xiaobei.yinghuaonline.com/xiaobei-api/"
captcha_url = BASE_URL + 'captchaImage'
# 登录
login_url = BASE_URL + 'login'
# 打卡
health_url = BASE_URL + 'student/health'
# header 请求头
HEADERS = {
    "user-agent": "iPhone10,3(iOS/14.4) Uninview(Uninview/1.0.0) Weex/0.26.0 1125x2436",
    "accept": "*/*",
    "accept-language": "zh-cn",
    "accept-encoding": "gzip, deflate, br"
}


def get_health_param(location, coord):
    # 体温随机为35.8~36.7
    temperature = str(random.randint(358, 367) / 10)
    # 生成随机后四位数
    rand = random.randint(1111, 9999)
    # 随机经度
    location_x = location.split(',')[0].split('.')[0] + '.' + location.split(',')[0].split('.')[1][0:2] + str(rand)
    # 随机纬度
    location_y = location.split(',')[1].split('.')[0] + '.' + location.split(',')[1].split('.')[1][0:2] + str(rand)
    location = location_x + ',' + location_y
    print('经纬度：{}, 打卡位置：{}'.format(location, coord))
    return {
        "temperature": temperature,
        "coordinates": coord,
        "location": location,
        "healthState": "1",
        "dangerousRegion": "2",
        "dangerousRegionRemark": "",
        "contactSituation": "2",
        "goOut": "1",
        "goOutRemark": "",
        "remark": "无",
        "familySituation": "1"
    }


def xiaobei_update(username, password, location, coord):
    print("\n"+username+"开始操作")
    flag = False

    # 获取验证信息
    try:
        print("开始获取验证信息")
        response = requests.get(url=captcha_url, headers=HEADERS)
        uuid = response.json()['uuid']
        showCode = response.json()['showCode']
        print("验证信息获取成功")
    except:
        print("验证信息获失败")
        return False

    # 使用验证信息登录
    try:
        print("正在登录小北平台")
        response = requests.post(url=login_url, headers=HEADERS, json={
            "username": username,
            "password": str(base64.b64encode(password.encode()).decode()),
            "code": showCode,
            "uuid": uuid
        })
        print("平台响应："+response.json()['msg'])
    except:
        print("登录失败")
        return False

    # 检测Http状态
    if response.json()['code'] != 200:
        print("登陆失败："+response.json()['msg'])
    else:
        try:
            print(username+"登陆成功，开始打卡")

            HEADERS['authorization'] = response.json()['token']
            response = requests.post(
                url=health_url, headers=HEADERS, json=get_health_param(location, coord))
            # print(response)
        except:
            print(username+"打卡失败")
        HEADERS['authorization'] = ''

    # 解析结果
    try:
        if "已经打卡" in response.text:
            print(username+"🎉今天已经打过卡啦！")
            flag = True
        elif response.json()['code'] == 200:
            print(username+"🎉恭喜您打卡成功啦！")
            flag = True
        else:
            print(username+"打卡失败，平台响应：" + response.json())
    except:
        return False
    return flag


#  打卡
def clock():
    # 定义基本信息的初始值
    count, failed, failed_username = 0, 0, ""
    # 循环打卡列表
    for i in array:
        if xiaobei_update(i[0], i[1], i[2], i[3]) == False:
            failed = failed + 1
            failed_username = failed_username + str(i[0]) + ",\n"
        count = count + 1
        time.sleep(1)

    if failed == 0:
        print("\n🎉恭喜您打卡成功啦！一共是" + str(count) + "人")
    else:
        print("\n😥共操作" + str(count) + "人,失败" + str(failed) + "人")
        print("失败账号：\n" + failed_username)


if __name__ == "__main__":
    while True:
        newtime = datetime.datetime.now().strftime('%w %H').split()
        seektime = int(newtime[0])
        hourtime = int(newtime[1])
        print(f'当前星期：{seektime}时间：{hourtime}点 ，设置运行时间为星期：{timeweek}当天： {timeing}点 运行')

        if int(seektime) == int(timeweek):
            if hourtime != int(timeing):
                print('当前不在运行时间段，但会默认会运行，之后时间会精确设置运行的时间')
            while True:
                clock()
                print('程序将在 ' + (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S") + ' 继续运行\n\n')  # 第一次显示的时间会不对，之后就应该对了
                time.sleep(60*60*24*6 + 60*60*(24-hourtime+int(timeing)))  # 七天后继续运行
        else:
            timsweek = int(timeweek)
            if seektime == 0:  # 如果当前星期天
                timer = timsweek - seektime
            elif timsweek == 0:  # 如果设置为星期天，不存在两个都为星期天
                timer = timsweek + 7 - seektime
            elif seektime < timsweek:
                timer = timsweek - seektime
            else:
                timer = timsweek + 7 - seektime
            runtime = 60*60*24*(timer-1) + 60*60*(24-hourtime+int(timeing))
            print(f'当前不在运行时间段,将在{runtime}秒后继续运行')
            time.sleep(runtime)
