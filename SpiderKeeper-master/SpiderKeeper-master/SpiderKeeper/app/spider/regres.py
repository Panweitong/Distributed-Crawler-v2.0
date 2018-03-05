# -*- coding: utf-8 -*-
from SpiderKeeper.app.spider.dataAnalyse import getCity_Money

__author__ = 'XMAN-YCX'
__project__ = 'Ultimately'
__date__ = '17/8/18 '
import re
import numpy as np
import pandas as pd
import MySQLdb
import jieba.analyse
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud,ImageColorGenerator,STOPWORDS
from PIL import Image

def job_condition(te):
    #保存待匹配的文本
    text = te
    global new_text
    global ck
    #开始匹配的关键字
    start_condition = ["职位要求","任职资格","任职要求","任职条件","岗位要求","人员要求","任职资格","应聘要求","优先条件"]
    text1 = str(text).replace(r"\n","")
    End = None
    for i in range(9):
        #查找开始位置
        Tag = re.search(start_condition[i],text1)
        #查找成功
        if Tag:
            start_index = Tag.start()+ 4
            # 记录新文本
            new_text = text1[start_index:]
            # 匹配结束标志
            End = re.search("。", new_text)
            break
        else:
            if i==8:
                #print("该招聘信息无法匹配.")
                pass

    if End:
        End_idnex = End.end()
    #获取最终文本
        end_text = new_text[:End_idnex]
        #print(end_text)
        ck = end_text.upper()
        # with open('description.txt', 'a') as f:
        #     f.write(end_text.upper() + "\n")
        return ck


def wordCloud():
    #连接MYSQL,获取数据，
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    df = pd.read_sql('select * from job_cache;', con=mysql_cn)
    mysql_cn.close()
    remark = df[['remark']]
    fuck = []
    for index, row in remark.iterrows():   # 获取每行的index、row
       data = row['remark']                 # 把结果返回给data
       k = job_condition(data)
       fuck.append(k)
    # 读入背景图片
    abel_mask = np.array(Image.open(r"C:\Users\Administrator\Desktop\SpiderKeeper-master\SpiderKeeper-master\SpiderKeeper\app\static\images\tupian1.png"))
    #设置停用词
    stop = []
    for line in open(r'C:\Users\Administrator\Desktop\SpiderKeeper-master\SpiderKeeper-master\SpiderKeeper\app\spider\stopWord.txt', 'r',encoding='utf-8'):
        STOPWORDS.add(line.strip())
    # 读取要生成词云的文件
    fk = ""
    for i in range(len(fuck)):
        if fuck[i]:
            fk += str(fuck[i])
    #text_from_file_with_apath = open('description.txt').read()

    # 通过jieba分词进行分词并通过空格分隔
    wordlist_after_jieba = jieba.cut(fk)
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
    # my_wordcloud.recolor(color_func=image_colors)

    # 以下代码显示图片
    plt.imshow(my_wordcloud)
    plt.axis("off")
    #plt.figure()
    # 保存词云
    my_wordcloud.to_file(r'C:\Users\Administrator\Desktop\SpiderKeeper-master\SpiderKeeper-master\SpiderKeeper\app\static\images\cloud.png')


def countAbiity():
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    df = pd.read_sql('select * from job_cache;', con=mysql_cn)
    mysql_cn.close()
    remark = df[['remark']]
    fuck = []
    for index, row in remark.iterrows():   # 获取每行的index、row
       data = row['remark']                 # 把结果返回给data
       k = job_condition(data)
       fuck.append(k)

    word_lst = []
    key_list = []
    for line in range(len(fuck)):  # 1.txt是需要分词统计的文档
        if fuck[line]:
            item = str(fuck[line]).strip('\n\r').split('\t')  # 制表格切分

            tags = jieba.analyse.extract_tags(item[0])  # jieba分词
            for t in tags:
                word_lst.append(t)
    #os.remove('description.txt')
    stop = {}
    for line in open(r'C:\Users\Administrator\Desktop\SpiderKeeper-master\SpiderKeeper-master\SpiderKeeper\app\spider\stopWord.txt','r',encoding='utf-8'):
        stop[line.strip()] = 0
    print(stop)

    word_dict = {}
    word_ability = {}
    with open("wordCount.txt", 'w') as wf2:  # 打开文件

        for item in word_lst:
            if item not in word_dict:  # 统计数量
                word_dict[item] = 1
            else:
                word_dict[item] += 1

        for key in word_dict:
            if key in stop:
                pass
            else:
                word_ability[key] = word_dict[key]

        #print(word_dict)
        sort = sorted(word_ability.items(), key=lambda item: item[1], reverse=True)
        city_sort = list(sort)
        city_list1 = dict(city_sort[0:20])
        #city_list1为职业技能需求
        print(city_list1)


        ability_value = {}
        avg_money = int(getCity_Money())
        sum_ability = sum(list(city_list1.values()))
        for item in city_list1:
            ability_value[item] = int((city_list1[item]/sum_ability)*avg_money)
        #  ability_value为职业技能价值
        print(ability_value)
    return city_list1,ability_value


if __name__ == '__main__':
    countAbiity()
    wordCloud()
