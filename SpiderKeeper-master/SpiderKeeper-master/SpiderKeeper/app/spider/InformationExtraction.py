# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup, Comment
import re
import json
import chardet
BLOCKS = 0
CHANGE_RATE = 0.6
MIN_LENGTH = 3

def getHtml(url):
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36"}
    page = requests.get(url,headers=headers)
    html = page.content
    return html

def nob(tag):
    regEx_html = "<[^>]+>" # 定义HTML标签的正则表达式
    tag = re.sub(regEx_html,'',tag)
    tag = re.sub("\t\n",'',tag)
    tag = re.sub("\s", '', tag)
    tag = re.sub("((\r\n)|\n)[\\s\t ]*(\\1)+", '', tag)
    tag = re.sub("^((\r\n)|\n)+", '', tag)
    tag = re.sub("    +| +|　+", '', tag)
    return tag

def getDensity(div):
    x = len(str(div))
    y = len(str(re.sub('\s', '', nob(str(div))))) + len(div.find_all("img")) * len(str(re.sub('\s', '', nob(str(div))))) * 0.4
    return y / x


def deleteLabel(html):
    regEx_script = "<script[^>]*?>[\\s\\S]*?<\\/script>"
    regEx_style = "<style[^>]*?>[\\s\\S]*?<\\/style>"
    regEx_html = "<[^>]+>"
    regEx_anno = "<!--[\\s\\S]*?-->"
    html = re.sub(regEx_script, '', html)
    html = re.sub(regEx_style, '', html)
    html = re.sub(regEx_html, "",html)
    html = re.sub(regEx_anno, "",html)
    html = re.sub("((\r\n)|\n)[\\s\t ]*(\\1)+", "\n",html)
    html = re.sub("^((\r\n)|\n)", "",html)
    html = re.sub("[ \t\x0B\f\r]", "", html)
    html = re.sub("    +| +|　+", "",html)
    return html

def splitBlock(text):
    groupMap = {}
    line = ""
    blocksLine = ""
    theCount = 0
    groupCount = 0
    count = 0
    tags = text.split('\n')
    for tag in tags:
        if (len(tag) > MIN_LENGTH):
            if (theCount <= BLOCKS):
                blocksLine += tag
                theCount+=1
            else:
                groupMap[groupCount] = blocksLine
                groupCount+=1
                blocksLine = tag
                theCount = 1
            count+=1
    if (theCount != 0):
        groupMap[groupCount] = blocksLine
    # print("一共" + str(len(groupMap)) + "个行块，数据行数一共有" + str(count))
    return groupMap

def judgeBlocks(maps):
    contentBlock = []
    currentBlock = len(str(maps.get(0)))
    lastBlock = 0
    for key in maps:
        if key == 0 and len(str(maps[key])) >= 7:
            contentBlock.append(key)
            continue
        lastBlock = currentBlock
        currentBlock = len(str(maps[key]))
        between = abs(currentBlock - lastBlock) / max(currentBlock, lastBlock)
        if (between >= CHANGE_RATE):
            contentBlock.append(key)
    matchNode = len(contentBlock)
    # print("一共有" + str(matchNode) + "峰值点")
    # print(contentBlock)
    lastContent = 0
    context = ""
    if (matchNode >= 2): #两个以上
        #开始
        result = ""
        for index in range(contentBlock[0],contentBlock[matchNode-1]+1):
            try:
                result += str(maps[index])+"\n"
            except:
                continue

    return str(result).replace("&gt;","").replace("应用中心","").replace("已投稿到：","").replace("此博主被推荐的博文：","").replace("文章评论(-)","").replace("文章总数","").replace("关注爱范儿微信号，连接热爱，关注这个时代最好的产品","").replace("新闻排行榜","")


def getInformation(url):
    # getHTML
    # url = 'http://news.163.com/17/0623/05/CNJGHH3A00018AOP.html'
    html = getHtml(url)
    # chardet.detect(str(html))
    soup = BeautifulSoup(html, "lxml")
    # 获取标题
    title = soup.title.text
    # title = re.split('-|_', title)[0]
    title = nob(title)
    # 网站简单的预处理取出js代码
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]
    for script in soup.find_all("script"):
        script.clear()
    for style in soup.find_all("style"):
        style.clear()
    for head in soup.find_all("head"):
        head.clear()
    for head in soup.find_all("a"):
        head.clear()
    for hid in soup.find_all(style=re.compile("display[\\s\\S]{0,3}none")):
        hid.clear()
    for div in soup.find_all(class_=re.compile(".*foot.*")):
        div.clear()
    for hid in soup.find_all(type=re.compile("hidden")):
        hid.clear()
    for footer in soup.find_all(["footer", "button","em","ul"]):
        footer.clear()
    # 文本密度预处理
    for div in soup.find_all(["div", "td"]):
        # 判断子集
        if len(div.find_all(["div", "td"])) > 0:  # 存在子集
            continue
        if getDensity(div) > 0.1 and len(nob(str(div))) >= 5:  # 指定一个阈值
            continue
        else:
            div.clear()
    html = str(soup)
    html = deleteLabel(html)
    map = splitBlock(html)
    # i = 0
    # for s in map:
    #     print(str(i)+" "+map[s])
    #     i = i + 1
    datas = {"title":title, "content":judgeBlocks(map), "status":1}
    json1 = json.dumps(datas, ensure_ascii=False, indent=1, sort_keys=True)
    return json1


def getInformationByHtml(html):
    soup = BeautifulSoup(html, "lxml")
    # 获取标题
    title = soup.title.text
    # title = re.split('-|_', title)[0]
    title = nob(title)
    # 网站简单的预处理取出js代码
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]
    for script in soup.find_all("script"):
        script.clear()
    for style in soup.find_all("style"):
        style.clear()
    for head in soup.find_all("head"):
        head.clear()
    for head in soup.find_all("a"):
        head.clear()
    for hid in soup.find_all(style=re.compile("display[\\s\\S]{0,3}none")):
        hid.clear()
    for div in soup.find_all(class_=re.compile(".*foot.*")):
        div.clear()
    for hid in soup.find_all(type=re.compile("hidden")):
        hid.clear()
    for footer in soup.find_all(["footer", "button","em","ul"]):
        footer.clear()
    # 文本密度预处理
    for div in soup.find_all(["div", "td"]):
        # 判断子集
        if len(div.find_all(["div", "td"])) > 0:  # 存在子集
            continue
        if getDensity(div) > 0.1 and len(nob(str(div))) >= 5:  # 指定一个阈值
            continue
        else:
            div.clear()
    html = str(soup)
    html = deleteLabel(html)
    map = splitBlock(html)
    datas = {"title":title, "content":judgeBlocks(map), "status":1}
    json1 = json.dumps(datas, ensure_ascii=False, indent=1, sort_keys=True)
    return json1
# url = 'http://news.ycwb.com/2017-08/23/content_25411903.htm'
# html = getHtml(url)
# print(getInformation(url))