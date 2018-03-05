# -*- coding: utf-8 -*-
__author__ = 'ZJM'
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider
from bs4 import BeautifulSoup
import json
import urllib.parse as urlparse
from fake_useragent import UserAgent
import requests
import time
from WuLiSpider.items import GoogleNewsItem
from tools import InformationExtraction
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import MySQLdb
ua = UserAgent()

def inset(state):
    conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="wulispider", charset="utf8")
    cursor = conn.cursor()
    cursor.execute(
        "insert state(id,"  # 产品TB编号
        "name,"  # 公司TB编号
        "state"
        ") VALUES(1, 'GoogleNews', '{0}') ON DUPLICATE KEY UPDATE state=VALUES(state)".format(
            str(state).replace("'","\"").replace("/","_")
        )
    )
    conn.commit()

class GoogleNewsSpider(RedisSpider):
    def __init__(self, allowed_domains=None,model=None, *args, **kwargs):
        super(GoogleNewsSpider, self).__init__(*args, **kwargs)
        self.isStop = 3
        # 绑定信号-延迟信号
        dispatcher.connect(self.spider_closed, signals.spider_idle)
        dispatcher.connect(self.spider_item, signals.item_scraped)
        # spider关闭时的逻辑

    def spider_closed(self, spider):
        if self.isStop == 3:
            return
        self.isStop = 0
        time.sleep(15)
        if self.isStop == 0:
            print(self.crawler.stats._stats)
            mystats = self.crawler.stats._stats
            mystats['isStop'] = 1
            mystats['msg'] = '采集结束'
            mystats['start_time'] = 0
            print(mystats)
            print(
                "我检测到爬虫关闭了-------------------------------------------------------------------------------------------")
            self.isStop = 3
            # 插数据进数据库
            inset(mystats)

            # 还没关闭

    def spider_item(self, spider):
        self.isStop = 1
        mystats = self.crawler.stats._stats
        mystats['isStop'] = 0
        mystats['msg'] = '正在采集'
        mystats['start_time'] = 0
        print(mystats)
        print("正在采集-------------------------------------------------------------------------------------------")
        # 插数据进数据库
        inset(mystats)

    # lpush googlenews:start_urls https://guge5.firstguo.com/search?num=100&tbm=nws&q=%E5%8C%97%E5%B8%88%E7%8F%A0&btnK=Google+%E6%90%9C%E7%B4%A2
    name = "googlenews"
    allowed_domains = []
    redis_key = 'googlenews:start_urls'

    def parse(self, response):
        #获取页码数
        soup = BeautifulSoup(response.text, "lxml")
        for div in soup.find_all('div', class_="g"):
            title = ' '
            url = ' '
            source = ' '
            date = ' '
            content = ' '
            if div.find("h3"):
                title = div.find("h3").text
            if div.find("h3").find("a"):
                url = div.find("h3").find("a").get('href')
            if div.find('span', class_="_OHs _PHs"):
                source = div.find('span', class_="_OHs _PHs").text
            if div.find('span', class_="f nsa _QHs"):
                date = div.find('span', class_="f nsa _QHs").text
            yield Request(url=url, callback=self.parse_detail, meta={"title":title,"source":source,"date":date})
    def parse_detail(self, response):
        try:
            print("---------------------------------------------------------")
            title = response.meta.get("title", "")  # 文章封面图
            url = response.url
            source = response.meta.get("source", "")  # 文章封面图
            date = response.meta.get("date", "")  # 文章封面图
            print(title)
            content = json.loads(InformationExtraction.getInformationByHtml(response.body.decode()))['content']
            print("============================================================================")
            news = GoogleNewsItem()
            news['title'] = title
            news['url'] = url
            news['source'] = source
            news['date'] = date
            news['content'] = content
            print("---------------------------------------------------------")
            yield news
        except Exception as e:
            print(e)
