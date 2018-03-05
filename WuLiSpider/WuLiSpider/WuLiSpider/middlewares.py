# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
# from tools.crawl_xici_ip import  GetIP
class WulispiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddlware(object):
    #随机更换user-agent
    def __init__(self, crawler):
        super(RandomUserAgentMiddlware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)
        request.headers.setdefault('User-Agent', get_ua())

# class RandomProxyMiddleware(object):
    # #动态设置ip代理
    # def process_request(self, request, spider):
    #     get_ip = GetIP()
    #     request.meta["proxy"] = get_ip.get_random_ip()
    #     # request.meta["proxy"] = "https://36.97.145.29:9999"
    #     print("使用了"+str(request.meta["proxy"]))

    # def process_response(self, request, response, spider):
    #     '''对返回的response处理'''
    #     # 如果返回的response状态不是200，重新生成当前request对象
    #     if response.status != 200:
    #         proxy = self.get_random_proxy()
    #         print("this is response ip:" + proxy)
    #         # 对当前reque加上代理
    #         request.meta['proxy'] = proxy
    #         return request
    #     return response


from scrapy.http import HtmlResponse
class JSPageMiddleware(object):
    def process_request(self, request, spider):
        if request.meta.get('js', 0) == 1:
            from tools import phantomjs
            port = "9000"
            cur = phantomjs.http_request(port)
            ua = UserAgent()
            response = cur.get(request.url,"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36")
            print("访问2:{0}".format(request.url))
            cur.get("about:blank","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36")
            return HtmlResponse(url=request.url, body=response.content.decode(), status=200, encoding="utf-8", request=request)



# # 初始化浏览器
    # def __init__(self, crawler):
    #     super(JSPageMiddleware, self).__init__()
    #     port = "8080"
    #     self.phantomjs = phantomjs.http_request(port)
    #     self.ua = UserAgent()
    #     self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")
    #     # self.browser = webdriver.Chrome(executable_path="C:/Users/Administrator/Desktop/chromedriver_win32/chromedriver.exe")
    #
    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(crawler)
    #
    # @classmethod
    # def process_request(cls, request, spider):
    #     if request.meta.get('js', 0) == 1:
    #         driver = webdriver.PhantomJS(executable_path="C:/Users/Administrator/Desktop/新建文件夹/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe")
    #         driver.get(request.url)
    #         import time
    #         time.sleep(10)
    #         content = driver.page_source.encode('utf-8')
    #         driver.quit()
    #         return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)

    # #请求动态网页
    # @classmethod
    # def process_request(self, request, spider):
    #     def get_ua():
    #         return getattr(self.ua, self.ua_type)
    #     print("1")
    #     if request.meta.get('js',0) == 1:
    #         # driver = webdriver.PhantomJS(executable_path='C:/Users/Administrator/Desktop/新建文件夹/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe')
    #         # browser = webdriver.Chrome(executable_path="D:/Temp/chromedriver.exe")
    #         # driver.get(request.url)
    #         # import time
    #         # time.sleep(1)
    #         # print("访问:{0}".format(request.url))
    #         # driver.quit()
    #         # return HtmlResponse(url=driver.current_url, body=driver.page_source, encoding="utf-8"
    #         #                     )
    #         print(request.url)
    #         response = self.phantomjs.get(request.url,get_ua())
    #         import time
    #         time.sleep(1)
    #         self.phantomjs.get("about:blank", get_ua())
    #         return HtmlResponse(url=request.url, body=response.content.decode(), encoding="utf-8", request=request)
            # return response


