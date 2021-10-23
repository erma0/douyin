# -*- encoding: utf-8 -*-
'''
@File    :   dy.py
@Time    :   2019/05/01 23:42:32
@Author  :   dagaocun
@Version :   1.0
@Link    :   https://dagaoya.github.io
@Desc    :   None
'''
import requests
import json
import os
import re
import csv

# 'Referer': https://www.iesdouyin.com/share/user/86134965662
HEADERS = {
    'Connection': 'keep-alive',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent':
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
}


# 本地获取sign，需要安装node
def get_sign_local(value):
    p = os.popen('node fuck-byted-acrawler.js %s' % value)
    return p.readlines()[0]


def get_real_address(url):
    if url.find('http') < 0:
        return url
    res = requests.get(
        url,
        headers={'user-agent': 'Aweme/27014 CFNetwork/974.2.1 Darwin/18.0.0'},
        allow_redirects=False)
    return res.headers['location'] if res.status_code == 302 else None


def get_dytk(uid):
    res = get_res('https://www.iesdouyin.com/share/user/' + uid)
    dytk = re.findall(r"dytk: '(.*?)'", res.content.decode('utf-8'))
    if len(dytk):
        return dytk[0]
    return None


def get_res(my_url):
    if my_url != '':
        res = requests.get(my_url, headers=HEADERS)
        return (res)
    else:
        return ('')


def get_uid(username):
    res = get_res('https://www.douyin.com/aweme/v1/wallet/userinfo/?uniq_id=' +
                  username + '&open_id=1')
    resJson = json.loads(res.content.decode('utf-8'))
    # nickname = resJson['data']['nickname']
    uid = resJson['data']['uid']
    if uid is not None:
        return uid
        # print(uid)
    else:
        # print('noId')
        return ''


def get_sign(uid):
    sign = get_res('http://47.100.105.29:3000/?id=' + uid)  # js解密接口，自己的服务器
    if sign is not None:
        return sign.content.decode('utf-8')
    return ''


'''
def get_user_videolist(username, uid, dytk, sign):
    max_cursor = '0'
    has_more = True
    i = 0

    f = open(username + '.csv', 'w', newline='', encoding='utf-8')
    csvwriter = csv.writer(f)
    csvwriter.writerow(['id', 'desc', 'uri'])

    while has_more:
        res = get_res(
            'https://www.iesdouyin.com/web/api/v2/aweme/post/?user_id=' + uid +
            '&count=21&max_cursor=' + max_cursor + '&aid=1128&_signature=' +
            sign + '&dytk=' + dytk)
        resJson = json.loads(res.content.decode('utf-8'))
        max_cursor_pre = str(resJson.get('max_cursor'))
        if max_cursor_pre == 'None':
            continue
        else:
            max_cursor = max_cursor_pre
            print(max_cursor)
            has_more = resJson['has_more']
            videolist = resJson['aweme_list']
            for video in videolist:
                if video.get('video'):
                    desc = video['desc']
                    uri = video['video']['play_addr']['uri']
                    realAddr = get_real_address(
                        'https://aweme.snssdk.com/aweme/v1/play/?video_id=' +
                        uri +
                        '&line=0&ratio=540p&media_type=4&vr_type=0&improve_bitrate=0'
                    )
                    csvwriter.writerow([str(i + 1), desc, realAddr])
                    print('{0:^5}{1:^40}{2}'.format(str(i + 1), uri, desc))
                    i += 1
    else:
        print('over')
    if i == 0:
        print('Thhere is No Video')
    return i
'''


def get_user_videolist(get_type, username, uid, dytk, sign):
    max_cursor = '0'
    has_more = True
    i = 0
    if get_type == 'user':
        url_path = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?user_id='
        f = open(username + '.csv', 'w', newline='', encoding='utf-8')
    elif get_type == 'favorite':
        url_path = 'https://www.iesdouyin.com/web/api/v2/aweme/like/?user_id='
        f = open(username + '_favorite.csv', 'w', newline='', encoding='utf-8')
    else:
        print('Type error!')
        return 0
    csvwriter = csv.writer(f)
    csvwriter.writerow(['id', 'desc', 'uri'])

    while has_more:
        res = get_res(url_path + uid + '&count=21&max_cursor=' + max_cursor +
                      '&aid=1128&_signature=' + sign + '&dytk=' + dytk)
        resJson = json.loads(res.content.decode('utf-8'))
        max_cursor_pre = str(resJson.get('max_cursor'))
        if max_cursor_pre == 'None':
            continue
        else:
            max_cursor = max_cursor_pre
            print(max_cursor)
            has_more = resJson['has_more']
            videolist = resJson['aweme_list']
            for video in videolist:
                if video.get('video'):
                    desc = video['desc']
                    uri = video['video']['play_addr']['uri']
                    realAddr = get_real_address(
                        'https://aweme.snssdk.com/aweme/v1/play/?video_id=' +
                        uri +
                        '&line=0&ratio=540p&media_type=4&vr_type=0&improve_bitrate=0'
                    )
                    csvwriter.writerow([str(i + 1), desc, realAddr])
                    print('{0:^5}{1:^40}{2}'.format(str(i + 1), uri, desc))
                    i += 1
    else:
        print('over')
    if i == 0:
        print('There is No Video')
    return i


def get_user_params(username):
    uid = get_uid(username)
    dytk = get_dytk(uid)
    sign = get_sign(uid)
    print(username, uid, dytk, sign)
    # 选择函数功能
    get_user_videolist('user', username, uid, dytk, sign)  # 获取用户视频
    # get_user_videolist('favorite', username, uid, dytk, sign)  # 获取用户的喜欢


print('Enter your Douyin ID：')
username = input()
get_user_params(username)
