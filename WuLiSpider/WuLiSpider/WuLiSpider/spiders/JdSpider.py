# -*- coding: utf-8 -*-
__author__ = 'ZJM'
from scrapy.http import Request
from urllib import parse
from scrapy_redis.spiders import RedisSpider
from bs4 import BeautifulSoup
from WuLiSpider.items import JsGoodsItem
from WuLiSpider.items import commentItem
import re
from tools import myTools
from scrapy import signals
import time
import json
from scrapy.xlib.pydispatch import dispatcher
import scrapy
import MySQLdb

def inset(state):
    conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="wulispider", charset="utf8")
    cursor = conn.cursor()
    cursor.execute(
        "insert state(id,"  # 产品TB编号
        "name,"  # 公司TB编号
        "state"
        ") VALUES(2, 'JD', '{0}') ON DUPLICATE KEY UPDATE state=VALUES(state)".format(
            str(state).replace("'","\"").replace("/","_")
        )
    )
    conn.commit()


class JdSpider(RedisSpider):
    def __init__(self, allowed_domains=None,model=None, *args, **kwargs):
        super(JdSpider, self).__init__(*args, **kwargs)
        self.isStop = 3
        # 绑定信号-延迟信号
        dispatcher.connect(self.spider_closed, signals.spider_idle)
        dispatcher.connect(self.spider_item, signals.item_scraped)

    def spider_closed(self, spider):
        if self.isStop == 3:
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
        mystats['start_time'] = 0
        mystats['msg'] = '正在采集'
        print(mystats)
        print("正在采集-------------------------------------------------------------------------------------------")
        # 插数据进数据库
        inset(mystats)

    name = "jd"
    allowed_domains = []
    redis_key = 'jd:start_urls'

    #lpush jd:start_urls http://search.jd.com/Search?keyword=%e9%a6%96%e9%a5%b0&enc=utf-8
    # 收集所有404的url以及404页面数
    def parse(self, response):
        #解析网页
        soup = BeautifulSoup(response.text, "lxml")
        # 获取页码
        nodes = soup.find("span",class_="fp-text")
        if nodes!=None and nodes.find("i"):
            nodes = nodes.find("i").text
        else:
            nodes = 10
        for index in range(1,int(nodes)+1):
        # for index in range(1,2):
            items = myTools.getJdLink(response.url,index)
            for item in items:
                yield Request(url="https://item.jd.com/{item}.html".format(item=item), callback=self.parse_goods, priority = 0)

    def parse_goods(self, response):
        soup = BeautifulSoup(response.body, "lxml")
        title = soup.title.text
        pu = soup.find(id="popbox")
        if pu != None and len(pu) > 0:
            pu = pu.find_all("div", class_="mt")[0]
            store = pu.a.text
            storeUrl = pu.a.get("href")
        else:
            pu = soup.find("ul", class_="p-parameter-list")
            if pu == None:
                store = ""
                storeUrl = ""
            else:
                pu = pu.find(text=re.compile("品牌|店铺"))
                if pu == None:
                    store = "京东自营"
                    storeUrl = ""
                else:
                    pu = pu.parent
                    store = pu.a.text
                    storeUrl = pu.a.get("href")

        url = response.url
        id = re.split("/", url)
        id = id[len(id) - 1]
        id = re.split("\.", id)[0]
        jd_goods_item = {}
        jd_goods_item["id"] = id
        jd_goods_item["name"] = title
        jd_goods_item["url"] = response.url
        jd_goods_item["price"] = 0
        jd_goods_item["remark"] = ""
        jd_goods_item["store"] = store
        jd_goods_item["storeUrl"] = storeUrl
        jd_goods_item["comments"] = 0

        temp = str(soup).split('commentVersion:')
        pattern = re.compile("[\'](\d+)[\']")
        if len(temp) < 2:
            jd_goods_item['commentVersion'] = -1
        else:
            a = temp[1]
            a = a.split(',')[0][1:-1]
            jd_goods_item['commentVersion'] = a

        url = "http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=" + str(id)
        yield Request(url, meta={'item': jd_goods_item}, callback=self.parse_getCommentnum, priority = 1)

    def parse_getCommentnum(self, response):
        item1 = response.meta['item']
        # response.body是一个json格式的
        js = json.loads(response.body.decode())
        item1['score1count'] = js['CommentsCount'][0]['Score1Count']
        item1['score2count'] = js['CommentsCount'][0]['Score2Count']
        item1['score3count'] = js['CommentsCount'][0]['Score3Count']
        item1['score4count'] = js['CommentsCount'][0]['Score4Count']
        item1['score5count'] = js['CommentsCount'][0]['Score5Count']
        item1['comments'] = js['CommentsCount'][0]['CommentCount']
        num = item1['id']  # 获得商品ID
        s1 = str(num)
        url = "http://pm.3.cn/prices/pcpmgets?callback=jQuery&skuids=" + s1 + "&origin=2"
        yield Request(url, meta={'item': item1}, callback=self.parse_price, priority = 2)

    def parse_price(self, response):
        item1 = response.meta['item']
        temp1 = str(response.body.decode()).split('jQuery([')
        s = temp1[1][:-4]  # 获取到需要的json内容
        js = json.loads(str(s))  # js是一个list
        if 'pcp' in js:
            item1['price'] = js['pcp']
        else:
            item1['price'] = js['p']

        jd_goods_item = JsGoodsItem()
        jd_goods_item["id"] = item1['id']
        jd_goods_item["name"] = item1['name']
        jd_goods_item["url"] = item1['url']
        jd_goods_item["price"] = item1['price']
        jd_goods_item["remark"] = ""
        jd_goods_item["store"] = item1['store']
        jd_goods_item["storeUrl"] = item1['storeUrl']
        jd_goods_item["comments"] = item1['comments']
        jd_goods_item["score1count"] = item1['score1count']
        jd_goods_item["score2count"] = item1['score2count']
        jd_goods_item["score3count"] = item1['score3count']
        jd_goods_item["score4count"] = item1['score4count']
        jd_goods_item["score5count"] = item1['score5count']
        jd_goods_item["commentVersion"] = item1['commentVersion']
        import datetime
        jd_goods_item["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield jd_goods_item
        #下面开始抓评论
        good_num = int(jd_goods_item["id"])
        comment_total = int(jd_goods_item["comments"])
        if comment_total % 10 == 0:  # 算出评论的页数，一页10条评论
            page = comment_total / 10
        else:
            page = comment_total / 10 + 1
        for k in range(0, int(page)):
            url = "http://sclub.jd.com/productpage/p-" + str(good_num) + "-s-0-t-3-p-" + str(k) \
                  + ".html?callback=fetchJSON_comment98vv" + jd_goods_item['commentVersion']
            yield Request(url, callback=self.parse_getComment, priority = 2)

    def parse_getComment(self, response):
        temp1 = response.body.decode('gbk')
        temp1 = str(temp1).split('productAttr')
        mystr = '{"productAttr' + temp1[1][:-2]
        js = json.loads(mystr)
        comments = js['comments']  # 该页所有评论
        for comment in comments:
            item1 = commentItem()
            item1['id'] = comment['guid']
            item1['userClientShow'] = comment['userClientShow']
            item1['user_name'] = comment['nickname']
            item1['user_ID'] = comment['id']
            item1['userProvince'] = comment['userProvince']
            item1['content'] = comment['content']
            item1['good_ID'] = comment['referenceId']
            item1['good_name'] = comment['referenceName']
            item1['date'] = comment['referenceTime']
            item1['replyCount'] = comment['replyCount']
            item1['score'] = comment['score']
            item1['status'] = comment['status']
            title = ""
            if 'title' in comment:
                item1['title'] = comment['title']
            item1['title'] = title
            userRegisterTime = ""
            if 'userRegisterTime' in comment:
                item1['userRegisterTime'] = comment['userRegisterTime']
            item1['userRegisterTime'] = userRegisterTime
            item1['productColor'] = comment['productColor']
            item1['productSize'] = comment['productSize']
            item1['userLevelName'] = comment['userLevelName']
            item1['isMobile'] = comment['isMobile']
            item1['days'] = comment['days']
            tags = ""

            if 'commentTags' in comment:
                for i in comment['commentTags']:
                    tags = tags + i['name'] + " "
            item1['commentTags'] = tags
            yield item1