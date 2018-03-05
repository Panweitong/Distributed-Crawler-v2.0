# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WulispiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class JsGoodsItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    price = scrapy.Field()
    date = scrapy.Field()
    remark = scrapy.Field()
    store = scrapy.Field()
    storeUrl = scrapy.Field()
    comments = scrapy.Field()
    score1count = scrapy.Field()
    score2count = scrapy.Field()
    score3count = scrapy.Field()
    score4count = scrapy.Field()
    score5count = scrapy.Field()
    commentVersion = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
            insert into jd_goods(id, name, url, price, remark, date,store,storeUrl,comments,score1count,score2count,score3count,score4count,score5count,commentVersion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE price=VALUES(price), date=VALUES(date);insert into jd_goods_cache(id, name, url, price, remark, date,store,storeUrl,comments,score1count,score2count,score3count,score4count,score5count,commentVersion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE price=VALUES(price), date=VALUES(date)
        """
        params = (self["id"], self["name"], self["url"], self["price"], self["remark"], self["date"], self["store"], self["storeUrl"], self["comments"], self["score1count"], self["score2count"], self["score3count"], self["score4count"], self["score5count"], self["commentVersion"],
                  self["id"], self["name"], self["url"], self["price"], self["remark"], self["date"], self["store"], self["storeUrl"], self["comments"], self["score1count"], self["score2count"], self["score3count"], self["score4count"], self["score5count"], self["commentVersion"])
        return insert_sql, params



class commentItem(scrapy.Item):
    id = scrapy.Field()  # 评论用户的名字
    user_name = scrapy.Field()  # 评论用户的名字
    user_ID = scrapy.Field()  # 评论用户的ID
    userProvince = scrapy.Field()  # 评论用户来自的地区
    content = scrapy.Field()  # 评论内容
    good_ID = scrapy.Field()  # 评论的商品ID
    good_name = scrapy.Field()  # 评论的商品名字
    date = scrapy.Field()  # 评论时间
    replyCount = scrapy.Field()  # 回复数
    score = scrapy.Field()  # 评分
    status = scrapy.Field()  # 状态
    title = scrapy.Field()
    userLevelId = scrapy.Field()
    userRegisterTime = scrapy.Field()  # 用户注册时间
    productColor = scrapy.Field()  # 商品颜色
    productSize = scrapy.Field()  # 商品大小
    userLevelName = scrapy.Field()  # 银牌会员，钻石会员等
    userClientShow = scrapy.Field()  # 来自什么 比如来自京东客户端
    isMobile = scrapy.Field()  # 是否来自手机
    days = scrapy.Field()  # 天数
    commentTags = scrapy.Field()  # 标签
    def get_insert_sql(self):
        insert_sql = """
            insert into jd_comment(id,user_name, user_ID, userProvince, content, good_ID, good_name,date,replyCount,score,status,title,userRegisterTime,productColor,productSize,userLevelName,userClientShow,isMobile,days,tags) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content)
        """
        params = (self["id"],self["user_name"], self["user_ID"], self["userProvince"], self["content"], self["good_ID"], self["good_name"], self["date"], self["replyCount"], self["score"], self["status"], self["title"], self["userRegisterTime"], self["productColor"], self["productSize"], self["userLevelName"], self["userClientShow"], self["isMobile"], self["days"], self["commentTags"])
        return insert_sql, params


class NewsItem(scrapy.Item):
    # id = scrapy.Field()
    title = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
            insert into news_content(title, source, url, content, date) VALUES ( %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), date=VALUES(date);insert into news_content_cache(title, source, url, content, date) VALUES ( %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), date=VALUES(date)
        """
        params = (self["title"], self["source"], self["url"], self["content"], self["date"],self["title"], self["source"], self["url"], self["content"], self["date"])
        return insert_sql, params

class JobItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    money = scrapy.Field()
    location = scrapy.Field()
    education = scrapy.Field()
    experience = scrapy.Field()
    language = scrapy.Field()
    age = scrapy.Field()
    remark = scrapy.Field()
    comId = scrapy.Field()
    comName = scrapy.Field()
    comRemark = scrapy.Field()
    comIndustry = scrapy.Field()
    comSize = scrapy.Field()
    comAddress = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into job(id, name, url, money, location,education,experience,language,age,remark,comId,comName,comRemark,comIndustry,comSize,comAddress) VALUES ( %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s )
            ON DUPLICATE KEY UPDATE name=VALUES(name);insert into job_cache(id, name, url, money, location,education,experience,language,age,remark,comId,comName,comRemark,comIndustry,comSize,comAddress) VALUES ( %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s )
            ON DUPLICATE KEY UPDATE name=VALUES(name)
        """
        params = (self["id"], self["name"], self["url"], self["money"], self["location"],self["education"], self["experience"], self["language"], self["age"], self["remark"], self["comId"], self["comName"], self["comRemark"], self["comIndustry"], self["comSize"], self["comAddress"],
                  self["id"], self["name"], self["url"], self["money"], self["location"],self["education"], self["experience"], self["language"], self["age"], self["remark"], self["comId"], self["comName"], self["comRemark"], self["comIndustry"], self["comSize"], self["comAddress"])
        return insert_sql, params

class GoogleNewsItem(scrapy.Item):
    # id = scrapy.Field()
    title = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
            insert into google_news(title, source, url, content, date) VALUES ( %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content);insert into google_news_cache(title, source, url, content, date) VALUES ( %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content)
        """
        params = (self["title"], self["source"], self["url"], self["content"], self["date"],
                  self["title"], self["source"], self["url"], self["content"], self["date"])
        return insert_sql, params
