# -*- coding: utf-8 -*-
__author__ = 'ZJM'

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "jd"])

from selenium import webdriver
# browser = webdriver.PhantomJS(executable_path="C:/Users/Administrator/Desktop/chromedriver_win32/chromedriver.exe")
# browser.get("http://www.baidu.com")
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "news","-a","allowed_domains=news.sina.com.cn","-a","model=http://news.sina.com.cn/o/2017-06-30/doc-ifyhrttz1774544.shtml;http://news.sina.com.cn/c/nd/2017-06-30/doc-ifyhrxsk1479209.shtml;http://news.sina.com.cn/c/nd/2017-06-30/doc-ifyhrxsk1469545.shtml;http://news.sina.com.cn/china/xlxw/2017-06-29/doc-ifyhrxsk1455471.shtml;http://sky.news.sina.com.cn/2015-03-20/094158560.html;http://slide.news.sina.com.cn/s/slide_1_86058_173547.html"])

# execute(["scrapy", "crawl", "liepin"])
# execute(["scrapy", "crawl", "googlenews"])