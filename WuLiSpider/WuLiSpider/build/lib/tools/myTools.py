from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup, Comment
ua = UserAgent()

#请求网页
def getJdHtml(url,referer):
    headers = {"User-Agent": ua.random,
               "Referer": referer
               }
    try:
        page = requests.get(url, headers=headers, timeout=10)
        html = page.content
        return html
    except Exception as e:
        print(e)

def getJdLink(url,index):
    url1 = url + "&page=" + str(index * 2 - 1)
    html1 = getJdHtml(url1, "https://www.jd.com/")
    soup1 = BeautifulSoup(html1, "lxml")
    lis = soup1.find_all("li",class_='gl-item')
    itemsList = []
    for li in lis:
        item = {}
        itemsList.append(li.get('data-sku'))
        # print (li.get('data-sku'))
    #第二页
    url2 = str(url).replace("Search","s_new.php")+"&qrst=1&rt=1&stop=1&vt=2&bs=1&s=31&scrolling=y&tpl=1_M&page="+str(index * 2)+"&show_items=" + ",".join(itemsList)
    html2 = getJdHtml(url2, url1)
    soup2 = BeautifulSoup(html2, "lxml")
    lis = soup2.find_all("li", class_='gl-item')
    for li in lis:
        itemsList.append(li.get('data-sku'))
        # print (li.get('data-sku'))
    return itemsList