import base64
import random
import requests
import time
import datetime


# 定义运行时间，24小时制
timeing = '7'  # 为了不浪费电脑性能，使用小时制，会运行两次，为了防止时间差导致没有运行

# 设置账号 密码
array = [
    ["1767777777", "123456"],
]

# 东区宿舍 经纬度
LOCATION = "109.632015,23.239991"
# 位置，可选通过接口获取
COORD = "中国-湖北省-武汉市-江夏区"

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


def get_health_param(coord):
    # 体温随机为35.8~36.7
    temperature = str(random.randint(358, 367) / 10)
    # 107.807008,26.245838
    rand = random.randint(1111, 9999)
    # 经度
    location_x = LOCATION.split(',')[0].split(
        '.')[0] + '.' + LOCATION.split(',')[0].split('.')[1][0:2] + str(rand)
    # 纬度
    location_y = LOCATION.split(',')[1].split(
        '.')[0] + '.' + LOCATION.split(',')[1].split('.')[1][0:2] + str(rand)
    location = location_x + ',' + location_y
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


def xiaobei_update(username, password):
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
        # print(response)
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
                url=health_url, headers=HEADERS, json=get_health_param(COORD))
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


if __name__ == "__main__":
    count = 0
    failed = 0
    failed_username = ""
    nowtime = datetime.datetime.now().strftime('%H')
    while True:
        print(f'程序将在{timeing}点和{str(int(timeing)+1)}点运行')
        if nowtime == timeing or timeing == str(int(nowtime)-1):
            # 循环打卡列表
            for i in array:
                if xiaobei_update(i[0], i[1]) == False:
                    failed = failed+1
                    failed_username = failed_username+str(i[0])+",\n"
                count = count+1
                time.sleep(1)

            if failed == 0:
                title = "\n🎉恭喜您打卡成功啦！一共是"+str(count)+"人"
            else:
                title = "\n😥共操作"+str(count)+"人,失败"+str(failed)+"人"
                message = "失败账号：\n"+failed_username
            print(title)
            count, failed = 0, 0
            print('程序将在 ' + (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
                "%Y-%m-%d ") + timeing + '点和' + str(int(timeing)+1) + '点继续运行\n\n')
        else:
            print('当前不在这个时间段，程序将不会运行')
        time.sleep(3600)
