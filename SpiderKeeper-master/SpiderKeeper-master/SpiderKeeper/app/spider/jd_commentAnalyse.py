# -*- coding:utf-8 -*-

import jieba
import numpy as np
import pandas as pd
import MySQLdb
import re
import json
import matplotlib.pyplot as plt
from wordcloud import WordCloud,ImageColorGenerator,STOPWORDS
from PIL import Image

#获取商品评分
def Goods_com(id):
    # 连接MYSQL,获取数据，
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    sql = 'select * from jd_goods WHERE id='+str(id)
    df = pd.read_sql(sql, con=mysql_cn)
    mysql_cn.close()
    #总评论，差评，中评，好评
    gd = df[['comments','score1count','score4count','score5count']]
    score_com = {}
    a = dict(gd.loc[0])
    score_com['总评论数:'] = a['comments']
    score_com['好评数:'] = a['score5count']
    score_com['中评数:'] = a['score4count']
    score_com['差评数:'] = a['score1count']
    good_rate = '%.5f' % ((int(a['score5count'])/int(a['comments']))*100)
    score_com['好评率:'] = str(good_rate)+"%"
    print(score_com)


#获取用户等级
def Comments_level(id):
    # 连接MYSQL,获取数据，
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    sql = 'select * from jd_comment WHERE good_ID='+str(id)+";"
    df = pd.read_sql(sql, con=mysql_cn)
    mysql_cn.close()
    gd = df[['userLevelName']]
    Level_dict = {}
    result = {}
    if  len(gd) == 0:
        result['state'] = '失败'
        result['result'] = Level_dict
        #------------------------无数据的返回值--------------------
        return result
    #用户等级
    Level = list(gd['userLevelName'])

    # 统计频数
    for item in Level:
        if item not in Level_dict:
            Level_dict[item] = 1
        else:
            Level_dict[item] += 1
    if 'PLUS会员[试用]' in Level_dict:
        if 'PLUS会员' in Level_dict:
            Level_dict['PLUS会员'] = Level_dict['PLUS会员']+Level_dict['PLUS会员[试用]']
            Level_dict.pop('PLUS会员[试用]')
    #-------------------返回购买该商品的用户等级-----------------
    #print(Level_dict)
    result['state'] = '成功'
    result['result'] = Level_dict
    print(result)
    return json.dumps(result,ensure_ascii=False)


def Comment_client(id):
    # 连接MYSQL,获取数据，
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    sql = 'select * from jd_comment WHERE good_id=' + str(id)
    df = pd.read_sql(sql, con=mysql_cn)
    mysql_cn.close()

    #购买途径（客户端）
    Client = df[['userClientShow']]
    #总数量
    count = len(Client)
    clean_client = df[df.userClientShow != '']
    cl = list(clean_client['userClientShow'])
    #PC端人数
    pc_count = count- len(clean_client)

    Client_dict = {'来自京东iPhone客户端':0,'来自京东Android客户端':0,'来自微信购物':0,'来自京东iPad客户端':0}
    # 统计频数
    for item in cl:
        if item not in Client_dict:
            Client_dict[item] = 1
        else:
            Client_dict[item] += 1
    Client_user = {}
    Client_user['iPhone客户端'] = Client_dict['来自京东iPhone客户端']
    Client_user['Android客户端'] = Client_dict['来自京东Android客户端']
    Client_user['微信购物'] = Client_dict['来自微信购物']
    Client_user['iPad客户端'] = Client_dict['来自京东iPad客户端']
    Client_user['PC客户端'] = pc_count
    #-------------------返回购买途径(客户端)--------------
    print(Client_user)
    return json.dumps(Client_user)

#返回购买后评价的时间----------这个不同管--------------------不需要这个-------------
def getDay(id):
    # 连接MYSQL,获取数据，
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    sql = 'select * from jd_comment WHERE good_ID=' + str(id)
    df = pd.read_sql(sql, con=mysql_cn)
    mysql_cn.close()
    gd = df[['days']]
    day = list(gd['days'])

    day_dict = {}
    # 统计频数
    for item in day:
        if item not in day_dict:
            day_dict[item] = 1
        else:
            day_dict[item] += 1

    count  = np.math.ceil(len(day_dict.keys()) / 3)

    sort = sorted(day_dict.items(), key=lambda item: item[1], reverse=True)
    days_sort = list(sort)
    days_list = dict(days_sort[0:count])
    #---------------------返回购买后评价的时间-----------------
    print(days_list)

#该商品购买时间分布
def getDate(id):
    # 连接MYSQL,获取数据，
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    sql = 'select * from jd_comment WHERE good_ID=' + str(id) + ";"
    df = pd.read_sql(sql, con=mysql_cn)
    mysql_cn.close()
    gd = df[['date']]
    for index, row in gd.iterrows():
        # 处理薪酬数据
        row['date'] = row['date'].split(' ')
        row['date'] = row['date'][0]
        row['date'] = row['date'].split('-')
        if row['date'][0] != '2017':
            row['date'] = '3'
        else:
            row['date']= str(row['date'][1]).replace("0","")

    #print(gd)
    date_dict = {}
    # 统计频数
    for item in list(gd['date']):
        if item not in date_dict:
            date_dict[item] = 1
        else:
            date_dict[item] += 1
    #------------------返回购买月份--------------------
    #print(date_dict)
    date = [0,0,0,0,0,0,0,0]
    for i in range(9):
        for item in date_dict:
            if int(item)-1 == i:
                date[i] = date_dict[item]
    #--------------返回一个LIST数组-------------
    print(date)
    return json.dumps(date, ensure_ascii=False)


#分析购买该商品给予的对象
def getRole(id):
    # 连接MYSQL,获取数据，
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    sql = 'select * from jd_comment WHERE good_id= '+str(id)
    df = pd.read_sql(sql, con=mysql_cn)
    mysql_cn.close()
    rd = df[['content']]
    role_dict = {'买给老公': 0, '买给老婆': 0, '买给男朋友': 0, '买给女朋友': 0}
    #print(rd)
    for index, row in rd.iterrows():
        # 处理薪酬数据
        if re.search('老公',row['content']):
            role_dict['买给老公'] += 1
        elif re.search('老婆',row['content']):
            role_dict['买给老婆'] += 1
        elif re.search('男朋友', row['content']):
            role_dict['买给男朋友'] += 1
        elif re.search('女朋友', row['content']):
            role_dict['买给女朋友'] += 1
    #----------------返回购买人群-------------------------
    print(role_dict)
    return json.dumps(role_dict, ensure_ascii=False)


def wordCloud1(id):
    # 连接MYSQL,获取数据，
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    sql = 'select * from jd_comment WHERE good_id='+str(id) + " and score=5;"
    df = pd.read_sql(sql, con=mysql_cn)
    mysql_cn.close()
    word = df[['content']]
    # 读取要生成词云的文件
    word_list = list(word['content'])
    word_str = ""

    for item in range(len(word_list)):
       word_str += str(word_list[item])
       #print(word_str)

    # 读入背景图片
    abel_mask = np.array(Image.open(r"C:\Users\Administrator\Desktop\SpiderKeeper-master\SpiderKeeper-master\SpiderKeeper\app\static\images\tupian1.png"))
    #设置停用词
    stop = []
    #for line in open('stopWord.txt', 'r'):
    STOPWORDS.add('京东')
    STOPWORDS.add('商品')
    STOPWORDS.add('价格')
    STOPWORDS.add('hellip')
    # fk = ""
    # for i in range(len(fuck)):
    #     if fuck[i]:
    #         fk += str(fuck[i])
    #text_from_file_with_apath = open('description.txt').read()

    # 通过jieba分词进行分词并通过空格分隔
    wordlist_after_jieba = jieba.cut(word_str)
    wl_space_split = " ".join(wordlist_after_jieba)
    # my_wordcloud = WordCloud().generate(wl_space_split) 默认构造函数
    my_wordcloud = WordCloud(
            background_color='white',  # 设置背景颜色
            mask=abel_mask,  # 设置背景图片
            max_words=80,  # 设置最大现实的字数
            stopwords=STOPWORDS,
            font_path='simkai.ttf',
            # 设置字体格式，如不设置显示不了中文
            max_font_size = 120,  # 设置字体最大值
            random_state = 40,  # 设置有多少种随机生成状态，即有多少种配色方案
            width=400,
            height=400, #设置图片的大小
            scale = .7,

    ).generate(wl_space_split)

    # 根据图片生成词云颜色
    image_colors = ImageColorGenerator(abel_mask)
    # 以下代码显示图片
    plt.imshow(my_wordcloud)
    plt.axis("off")
    # 保存词云
    my_wordcloud.to_file(r'C:\Users\Administrator\Desktop\SpiderKeeper-master\SpiderKeeper-master\SpiderKeeper\app\static\images\cloud_comm.png')


if __name__ == '__main__':
    # Comments_level(1085687)
    wordCloud1(11301756)
    # getDate(10803033)
    # getRole(11068575657)