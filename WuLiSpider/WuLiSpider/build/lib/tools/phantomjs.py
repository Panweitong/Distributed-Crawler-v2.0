#! -*- coding:utf-8 -*-
import requests
import hashlib
import base64
from multiprocessing.dummy import Pool
from bs4 import BeautifulSoup
import re
import time
import json
class http_request:
    def __init__(self, port="8080"):
        self.url = "http://localhost:" + port

    def get(self,url,ua):
        '''
        获取网页源代码
        '''
        default_options = {
            'method': 'GET',
            'headers': {},
            'allow_redirects': True,
            'use_gzip': True,
            'timeout': 120,
            'proxy': '0',#"'115.46.146.76:8123:HTTP',
            'url': '',
            'load_images': False,  # 不加载图片
        }
        default_options["url"] = url
        default_options["headers"]["User-Agent"] = ua
        js = json.dumps(default_options, ensure_ascii=False, indent=1, sort_keys=True)
        try:
            response = requests.post(self.url, data=js, timeout=30)
            return response
        except requests.exceptions.ConnectionError:
            print("requests connection error")
        except Exception as e:
            print(e)
        return


if __name__ == "__main__":
    port = "9000"
    cur = http_request(port)
    start = time.clock()
    response = cur.get("https://item.jd.com/12087181.html","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36")
    # print(response.content.decode())
    end = time.clock()
    print("单个用时" + str(end - start) + "秒")
    soup = BeautifulSoup(response.content.decode(), "lxml")
    title = soup.title.text
    # print(title)

    pu = soup.find("ul",class_="p-parameter-list")
    pu = pu.find(text=re.compile("品牌"))
    pu = pu.parent
    pus = pu.a.text
    a = pu.a.get("href")
    print(pus)
    print(a)





    # start = time.clock()
    # for i in range(10):
    #     cur.getwebbody("https://item.jd.com/4674884.html")
    #     end = time.clock()
    # print("单线程加载10个JD网页用时" + str(end - start) + "秒")
    #
    #
    #
    # start = time.clock()
    #
    # def test(domain):
    #     print("Result_url is ", cur.getwebbody(domain))
    # pool = Pool(processes=10)
    # for domain in domain_list:  # 并发下发任务
    #     pool.apply_async(test, args=(domain,))  # 维持执行的进程总数为10，当一个进程执行完后添加新进程.
    # pool.close()
    # pool.join()
    # end = time.clock()
    # print("并发加载10个JD网页用时" + str(end - start) + "秒")