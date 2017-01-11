"""
    author = lawtech
    Unsplash图片爬虫：利用Unsplash Api
"""
# coding = utf-8

import requests
from urllib.request import urlopen
import os

def spider_pic(page_start, page_end):
    while page_start < page_end:
        data = {
            'client_id': 'be9a9b50f86ad446ef7816b881e5b42eb0844d24863a73af237435ee11e6a128',
            'page': page_start
        }
        r = requests.get('https://api.unsplash.com/photos', params= data)
        print("requests_url:" + r.url + "...")
        # print(r.status_code)
        response = r.json()
        for p in response:
            pic_url = p['urls']['full']
            pic_id = p['id']
            print("downloading:" + pic_url + "...")
            # fetching picture
            imgData = urlopen(pic_url).read()
            fileName = os.getcwd() + '/Unsplash/' + pic_id + '.jpg'
            if os.path.exists(str(fileName)):
                print("已经下载过该图片")
            else:
                with open(fileName, 'wb+') as f:
                    f.write(imgData)
                    print('已下载图片：{}，请求的 URL 为：{}'.format(fileName, pic_url))
        page_start += 1

if __name__ == '__main__':
    n1 = int(input("请输入所需下载的图片页面起始页： "))
    n2 = int(input("请输入所需下载的图片页面终止页： "))
    spider_pic(n1, n2)


