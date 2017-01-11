"""
    author = lawtech
    电影天堂电影信息爬虫
"""
# coding = utf-8

from urllib.request import urlopen
import re
from bs4 import BeautifulSoup


# 获取电影地址列表
def queryMovieDict(n, movieDict):
    for i in range(1, n+1):
        url = 'http://www.dytt8.net/html/gndy/dyzz/list_23_{}.html'.format(i)
        html = urlopen(url).read().decode('gb2312', 'ignore')
        bsObj = BeautifulSoup(html, "html.parser")
        for tag in bsObj.select('a[class="ulink"]'):
            pattern = re.compile('.*?(《.*?》).*?')
            name = re.search(pattern, tag.text).group(1)
            movieDict[name] = 'http://www.dytt8.net' + tag['href']


# 获取电影信息
def queryMovieInfo(movieDict):
    for name, url in movieDict.items():
        print('电影URL: ' + url)
        print('电影名称: ' + name)
        html = urlopen(url).read().decode('gb2312', 'ignore')
        movieContent = re.findall(r'<div class="co_content8">(.*?)</tbody>', html, re.S)
        pattern = re.compile('<ul>(.*?)<tr>', re.S)
        movieDate = re.findall(pattern, movieContent[0])
        if (len(movieDate) > 0):
            movieDate = movieDate[0].strip() + ''
        else:
            movieDate = ''
        print('电影发布时间: ' + movieDate[-10:])
        pattern = re.compile('<br /><br />(.*?)<br /><br /><img')
        movieInfo = re.findall(pattern, movieContent[0])
        if (len(movieInfo) > 0):
            movieInfo = movieInfo[0] + ''
            # 删除<br />标签
            movieInfo = movieInfo.replace("<br />", "")
            # 根据 ◎ 符号拆分
            movieInfo = movieInfo.split('◎')
        else:
            movieInfo = ""
        print("电影基础信息: ")
        for item in movieInfo:
            print(item)
        # 电影海报
        pattern = re.compile('<img.*? src="(.*?)".*? />', re.S)
        movieImg = re.findall(pattern, movieContent[0])
        if (len(movieImg) > 0):
            movieImg = movieImg[0]
        else:
            movieImg = ""
        print("电影海报: " + movieImg)
        pattern = re.compile('<td style="WORD-WRAP: break-word" bgcolor="#fdfddf"><a href="(.*?)">.*?</a></td>', re.S)
        movieDownUrl = re.findall(pattern, movieContent[0])
        if (len(movieDownUrl) > 0):
            movieDownUrl = movieDownUrl[0]
        else:
            movieDownUrl = ""
        print("电影下载地址：" + movieDownUrl + "")
        print("------------------------------------------------\n\n\n")


if __name__ == '__main__':
    n = int(input("请输入所需抓取的电影页数: "))
    movieDict = {}
    print("开始抓取电影数据");
    queryMovieDict(n, movieDict)
    print(len(movieDict))
    queryMovieInfo(movieDict)
    print("结束抓取电影数据")
