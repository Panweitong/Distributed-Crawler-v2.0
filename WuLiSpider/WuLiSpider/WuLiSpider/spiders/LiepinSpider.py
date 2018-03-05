# -*- coding: utf-8 -*-
__author__ = 'ZJM'
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider
from bs4 import BeautifulSoup, Comment
import json
import urllib.parse as urlparse
from fake_useragent import UserAgent
from WuLiSpider.items import JobItem
from scrapy import signals
import requests
from scrapy.xlib.pydispatch import dispatcher
from urllib import parse
import time
import MySQLdb
ua = UserAgent()

def inset(state):
    conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="wulispider", charset="utf8")
    cursor = conn.cursor()
    cursor.execute(
        "insert state(id,"  # 产品TB编号
        "name,"  # 公司TB编号
        "state"
        ") VALUES(0, 'leipin', '{0}') ON DUPLICATE KEY UPDATE state=VALUES(state)".format(
            str(state).replace("'","\"").replace("/","_")
        )
    )
    conn.commit()

class LagouSpider(RedisSpider):
    def __init__(self, allowed_domains=None,model=None, *args, **kwargs):
        self.isStop = 3
        super(LagouSpider, self).__init__(*args, **kwargs)
        #绑定信号-延迟信号
        dispatcher.connect(self.spider_closed, signals.spider_idle)
        dispatcher.connect(self.spider_item, signals.item_scraped)
    # spider关闭时的逻辑
    def spider_closed(self, spider):
        if self.isStop == 3 :
            return
        self.isStop = 0
        time.sleep(10)
        if self.isStop == 0:
            print(self.crawler.stats._stats)
            mystats = self.crawler.stats._stats
            mystats['isStop'] = 1
            mystats['msg'] = '采集结束'
            mystats['start_time'] = 0
            print(mystats)
            print("我检测到爬虫关闭了-------------------------------------------------------------------------------------------")
            self.isStop = 3
            #插数据进数据库
            inset(mystats)

    #还没关闭
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
    # lpush liepin:start_urls https://www.liepin.com/zhaopin/?key=%E6%88%BF%E5%9C%B0%E4%BA%A7&headckid=1


    name = "liepin"
    allowed_domains = ["liepin.com"]
    redis_key = 'liepin:start_urls'

    # 收集所有404的url以及404页面数
    def parse(self, response):
        #获取页码数
        soup = BeautifulSoup(response.text, "lxml")
        print(response.url)
        lasta = soup.find("a",class_="last").get('href')
        nums = urlparse.parse_qs(lasta.split('?')[1])
        nums = nums['curPage'][0]
        for index in range(1,int(nums)+1):
            curUrl = response.url + "&curPage=" + str(index)
            headers = {"User-Agent": ua.random}
            page = requests.get(curUrl, headers=headers, timeout=20)
            html = page.content
            soup = BeautifulSoup(html, "lxml")
            ul = soup.find('ul', class_="sojob-list")
            for li in ul.find_all("li"):
                a = li.find('a')['href']
                yield Request(url=parse.urljoin(response.url, a), callback=self.parse_detail)

    def parse_detail(self, response):
        id = ' '
        name = ' '
        url = ' '
        money = ' '
        location = ' '
        education = ' '
        experience = ' '
        language = ' '
        age = ' '
        remark = ' '
        comId = ' '
        comName = ' '
        comRemark = ' '
        comIndustry = ' '
        comSize = ' '
        comAddress = ' '
        try:
            asoup = BeautifulSoup(response.body.decode(), "lxml")
            comments = asoup.findAll(text=lambda text: isinstance(text, Comment))
            [comment.extract() for comment in comments]
            url = response.url
            id = str(url).split('/')[-1]
            id = str(id).split('.')[0]
            json1 = ''
            for i in asoup.find_all("script"):
                emString = i.get_text().strip()
                if u'var $CONFIG = {' in emString:
                    if u'1可投递用户，2草稿件里' in emString:
                        json1 = i.text[23:]
                        json1 = str(json1)[:len(json1) - 29]
                        json1 = json1 + "}"
                    else:
                        json1 = i.text[20:]
                        json1 = str(json1)[:len(json1) - 3]
                    break
            json1 = str(json1).replace('\n', '').replace('\t', '').replace('\r', '').replace('\'', '\"').replace(' ',
                                                                                                                 '')
            myjson = json.loads(json1)
            name = myjson['job']['title']
            money = str(myjson['job']['salaryName']).replace('$', '-')
            location = myjson['job']['dqName']
            comName = myjson['job']['company']
            if asoup.find("div", class_='job-qualifications'):
                spans = asoup.find("div", class_='job-qualifications').find_all('span')
                education = spans[0].text
                experience = spans[1].text
                language = spans[2].text
                age = spans[3].text
            elif asoup.find("div", class_='resume clearfix'):
                spans = asoup.find("div", class_='resume clearfix').find_all('span')
                education = spans[0].text
                experience = spans[1].text
                language = spans[2].text
                age = spans[3].text

            if asoup.find("div", class_='job-item main-message'):
                remark = asoup.find("div", class_='job-item main-message').text
            elif asoup.find("div", class_='job-main main-message'):
                remark = asoup.find("div", class_='job-main main-message').text
            if asoup.find("div", class_='job-item main-message noborder'):
                comRemark = asoup.find("div", class_='job-item main-message noborder').text
            elif asoup.find("div", class_='content content-word'):
                comRemark = asoup.find("div", class_='content content-word').text
            if asoup.find("ul", class_='new-compintro'):
                uls = asoup.find("ul", class_='new-compintro').find_all('li')
                for ul in uls:
                    emString = ul.get_text().strip()
                    if u'行业' in emString:
                        comIndustry = ul.text.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '')[3:]
                    elif u'公司规模' in emString:
                        comSize = ul.text[5:]
                    elif u'公司地址' in emString:
                        comAddress = ul.text[5:]
            if asoup.find("div", class_='company-logo'):
                comId = asoup.find("div", class_='company-logo').find('a').get('href')

            job = JobItem()
            job['id'] = id
            job['name'] = name
            job['url'] = url
            job['money'] = money
            job['location'] = location
            job['education'] = education
            job['experience'] = experience
            job['language'] = language
            job['age'] = age
            job['remark'] = str(remark).replace("[", "").replace("]", "").replace("'", "")
            job['comId'] = comId
            job['comName'] = comName
            job['comRemark'] = str(comRemark).replace("[", "").replace("]", "").replace("'", "")
            job['comIndustry'] = comIndustry
            job['comSize'] = comSize
            job['comAddress'] = comAddress
            yield job
        except Exception as e:
            pass