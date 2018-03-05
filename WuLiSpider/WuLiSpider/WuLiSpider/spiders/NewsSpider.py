# -*- coding: UTF-8 -*-
__author__ = 'ZJM'

from scrapy.http import Request
from urllib import parse
from bs4 import BeautifulSoup
import re
from scrapy_redis.spiders import RedisSpider
from tools import InformationExtraction
from WuLiSpider.items import NewsItem
import json
class NewsSpider(RedisSpider):
    #启动前必须传参数 1.爬取的范围 2.需要爬取网站的详情页面模板（用,号做分隔符）
    def __init__(self, allowed_domains=None,model=None, *args, **kwargs):
        #处理模板
        model = str(model).split(";")
        models = []
        for m in model:
            models.append(re.sub("\d", "", m))
        super(NewsSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = [allowed_domains]
        self.models = models
        self.redis_key = allowed_domains + ':start_urls'
    name = "news"
    #lpush news.sina.com.cn:start_urls http://news.sina.com.cn/
    def parse(self, response):
        # 解析网页
        soup = BeautifulSoup(response.text, "lxml")
        # 获取所有的链接
        nodes = soup.find_all("a")
        # 遍历链接节点
        for node in nodes:
            # 链接地址
            href = str(node.get('href'))
            # 写规则
            if str(parse.urljoin(response.url, href)).find(str(self.allowed_domains[0])) >= 0 and re.sub("\d", "", parse.urljoin(response.url, href)) in self.models:
                yield Request(url=parse.urljoin(response.url, href), callback=self.parse_detail,priority = 10)
            elif str(parse.urljoin(response.url, href)).find(str(self.allowed_domains[0])) >= 0:
                yield Request(url=parse.urljoin(response.url, href), callback=self.parse)

    def parse_detail(self, response):
        newsItem = NewsItem()
        json1 = json.loads(InformationExtraction.getInformationByHtml(response.body.decode()))
        print(json1)
        # newsItem["id"] = "null"
        newsItem["title"] = json1["title"]
        newsItem["content"] = json1["content"]
        newsItem["url"] = response.url
        newsItem["source"] = str(self.allowed_domains[0])
        import datetime
        newsItem["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield newsItem

