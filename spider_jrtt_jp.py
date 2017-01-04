"""
    author = lawtech
    今日头条街拍图片爬虫
"""
# coding = utf-8

import re
import json
import time
import random

from pathlib import Path
from urllib import parse
from urllib import error
from urllib import request
from datetime import datetime
from http.client import IncompleteRead
from socket import timeout as socket_timeout

from bs4 import BeautifulSoup

def _create_dir(name):
    directory = Path(name)
    if not directory.exists():
        directory.mkdir()
    return directory

def _get_query_string(data):
    return parse.urlencode(data)

def get_article_urls(req, timeout = 10):
    with request.urlopen(req, timeout= timeout) as res:
        d = json.loads(res.read().decode()).get('data')
        if d is None:
            print("数据全部请求完毕......")
            return
        urls = [article.get('article_url') for article in d if article.get('article_url')]
        return urls

def get_photo_urls(req, timeout = 10):
    with request.urlopen(req, timeout= timeout) as res:
        soup = BeautifulSoup(res.read().decode(errors= 'ignore'), 'html.parser')
        article_main = soup.find('div', id= 'article-main')
        if not article_main:
            print("无法定位到文章主体...")
            return
        heading = article_main.h1.string
        if '街拍' not in heading:
            print("这不是街拍的文章！！！")
            return
        img_list = [img.get('src') for img in article_main.find_all('img') if img.get('src')]
        return heading, img_list

def save_photo(photo_url, save_dir, timeout=10):
    photo_name = photo_url.rsplit('/', 1)[-1] + '.jpg'
    save_path = save_dir / photo_name
    with request.urlopen(photo_url, timeout= timeout) as res, save_path.open('wb') as f:
        f.write(res.read())
        print('已下载图片：{dir_name}/{photo_name}，请求的 URL 为：{url}'.format(dir_name=save_path, photo_name=photo_name, url=photo_url))

if __name__ == '__main__':
    offset = 0
    ongoing = True
    root_dir = _create_dir('/Users/lawtech/PycharmProjects/pytest_3_5/spider_test/jiepai')
    request_headers = {
        'Referer': 'http://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
    }
    while ongoing:
        query_data = {
            'offset': offset,
            'format': 'json',
            'keyword': '街拍',
            'autoload': 'true',
            'count': 20,
            'cur_tab': 1
        }
        query_url = 'http://www.toutiao.com/search_content/' + '?' + _get_query_string(query_data)
        article_req = request.Request(query_url, headers=request_headers)
        article_urls = get_article_urls(article_req)
        # 如果不再返回数据，说明全部数据已经请求完毕，跳出循环
        if article_urls is None:
            break
        for a_url in article_urls:
            try:
                photo_req = request.Request(a_url, headers= request_headers)
                photo_urls = get_photo_urls(photo_req)
                if photo_urls is None:
                    continue
                article_heading, photo_urls = photo_urls
                dir_name = re.sub(r'[\\/:*?"<>|]', '', article_heading)
                download_dir = _create_dir(root_dir / dir_name)
                # 开始下载文章中的图片
                for p_url in photo_urls:
                    try:
                        save_photo(p_url, save_dir= download_dir)
                    except IncompleteRead as e:
                        print(e)
                        continue
            except socket_timeout:
                print("连接超时了，休息一下...")
                time.sleep(random.randint(15, 25))
                continue
            except error.HTTPError:
                continue
        # 一次请求处理完毕，将偏移量加 20，继续获取新的 20 篇文章。
        offset += 20



