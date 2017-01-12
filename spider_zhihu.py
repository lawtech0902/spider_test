"""
    author = lawtech
    知乎问题图片爬虫
"""
# coding = utf-8
import requests
import re
import json
import time
from PIL import Image
from io import StringIO
import http.cookiejar as cookielib
from urllib.request import urlretrieve
import os

api_url = 'https://www.zhihu.com/node/QuestionAnswerListV2'
login_url = 'https://www.zhihu.com/login/'
topic_url = 'https://www.zhihu.com/question/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}

session = requests.Session()
session.headers = headers
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("未登陆过，需先登录")


def get_xsrf(url="http://www.zhihu.com"):
    '''''_xsrf 是一个动态变化的参数'''
    global session
    index_url = url
    index_page = session.get(index_url)
    html = index_page.text
    pattern = r'name="_xsrf" value="(.*?)"'
    _xsrf = re.findall(pattern, html)
    return _xsrf[0]


def ImageScale(url, session=None):
    if session == None:
        session = requests.Session()
    file = StringIO(session.get(url).content)
    img = Image.open(file)
    img.show()


def get_captcha():
    global session
    t = str(int(time.time() * 1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r=%s&type=login' % t
    print(captcha_url)
    ImageScale(captcha_url, session)
    print('请输入验证码：')
    yzm = input()
    return yzm


def isLogin():
    global session
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url, allow_redirects=False).status_code
    if int(x=login_code) == 200:
        return True
    else:
        return False


def login(email, passwd):
    global session
    isemail = re.search('@', email)
    if isemail:
        loginurl = login_url + 'email'
        data = {'_xsrf': get_xsrf()
            , 'password': passwd
            , 'remember_me': 'true'
            , 'email': email}
    else:
        loginurl = login_url + 'phone_num'
        data = {'_xsrf': get_xsrf()
            , 'password': passwd
            , 'remember_me': 'true'
            , 'phone_num': email}
    try:
        login_page = session.post(loginurl, data=data)
        login_code = login_page.content
        print(login_page.status)
        print(login_code)
    except:
        data['captcha'] = get_captcha()
        login_page = session.post(loginurl, data=data)
        login_code = json.loads(login_page.content)
        print(login_code['msg'])
    session.cookies.save()


def get_pic_from_topic(id, offset):
    global session
    topicurl = topic_url + str(id)
    _xsrf = get_xsrf(topicurl)
    pic_re = re.compile('data-actualsrc="(.*?)"')
    inner_data = {"url_token": id
        , "pagesize": 10
        , "offset": offset
                  }
    data = {'method': 'next'
        , 'params': json.dumps(inner_data)
            }
    session.headers['Referer'] = topicurl
    session.headers['Host'] = 'www.zhihu.com'
    session.headers['Origin'] = 'https://www.zhihu.com'
    session.headers['X-Xsrftoken'] = _xsrf
    js_data = session.post(api_url, data=data)
    dat = json.loads(js_data.text)['msg']
    pictures = []
    for d in dat:
        pics = pic_re.findall(d)
        pictures.extend(pics)
    return pictures


def downloader(url, path):
    try:
        filename = url.split('/')[-1]
        save = os.path.join(path, filename)
        print('开始下载 ', filename)
        urlretrieve(url, filename=save)
    except Exception as e:
        print('下载出错，错误信息为：')
        print(e)


if __name__ == '__main__':
    email = '知乎账号'
    passwd = '知乎密码'
    is_login = isLogin()
    if not is_login:
        login(email, passwd)
    offset = 0
    pictures = []
    print("请输入知乎问题id!!!!!!!!!!!!!!")
    id = input()
    print('=====开始解析======')
    while 1:
        print("+++++正在解析第%d页+++++" % (offset / 10 + 1))
        pics = get_pic_from_topic(id, offset)
        if len(pics) == 0:
            print("解析完毕，共找到%d张图片" % len(pictures))
            break
        pictures.extend(pics)
        offset += 10
    print("=====开始下载图片=====")
    basepath = '/Users/lawtech/PycharmProjects/pytest_3_5/spider_test/zhihu'
    savepath = os.path.join(basepath, str(id))
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    for pic in pictures:
        downloader(pic, savepath)
    print("=====下载完毕,可以开撸啦！=====")
