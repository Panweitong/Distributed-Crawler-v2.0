# -*- coding:utf-8 -*-
import numpy as np
import pandas as pd
import MySQLdb
import  json

#统计行业与薪资之间的联系
def getComIndustry():
    com_work = df[['comIndustry','money']]
    clean_com = com_work[com_work.comIndustry != " "]
    clean_com = com_work[com_work.comIndustry != ""]
    clean_money = clean_com[clean_com.money != "面议"]

    for index, row in clean_money.iterrows():
        # 处理薪酬数据
        row['money'] = row['money'].replace('万', "").split('-')
        pp = int(int(row['money'][0]) + int(row['money'][1])) / 2
        row['money'] = pp

    comInd_list = list(clean_money['comIndustry'])
    Ind_dict = {}
    Ind_Num = {}

    # 统计频数
    for item in comInd_list:
        if item not in Ind_dict:
            Ind_dict[item] = 1
        else:
            Ind_dict[item] += 1

    for i in list(Ind_dict.keys()):
        Ind_Num[i] = 0

    for item in list(Ind_dict.keys()):
        # print(item)
        for i in range(len(comInd_list)):
            if item == list(clean_money['comIndustry'])[i]:
                Ind_Num[item] += int(list(clean_money['money'])[i])
            else:
                pass

    for item in Ind_Num:
        if item == " ":
            pass
        else:
            Ind_Num[item] = int((Ind_Num[item] / Ind_dict[item]) / 12 * 10000)
    print(Ind_Num)


#统计学历和薪资的关系
def getEdu_Money():
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    df = pd.read_sql('select * from job_cache;', con=mysql_cn)
    mysql_cn.close()
    edu_money = df[['education','money']]
    a = edu_money[edu_money.money != '面议']

    for index, row in a.iterrows():
        # 处理薪酬数据
        row['money'] = row['money'].replace('万', "").split('-')
        pp = int(int(row['money'][0]) + int(row['money'][1])) / 2
        row['money'] = pp

    edu_list = list(a['education'])
    edu_dict = {}
    edu_Num = {}

    #统计频数
    for item in edu_list:
        if item not in edu_dict:
            edu_dict[item] = 1
        else:
            edu_dict[item] += 1
    
    for i in list(edu_dict.keys()):
        edu_Num[i] = 0


    for item in list(edu_dict.keys()):
        # print(item)
        for i in range(len(a)):
            if item == list(a['education'])[i]:
                edu_Num[item] += int(list(a['money'])[i])
            else:
                pass

    for item in edu_Num:
        edu_Num[item] = int((edu_Num[item] / edu_dict[item]) / 12 * 10000)
    print(edu_Num)
    return json.dumps(edu_Num, ensure_ascii=False)


#全国平均薪酬(元／月)和各市平均工资前10
def getAvg_Money():
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    df = pd.read_sql('select * from job_cache;', con=mysql_cn)
    mysql_cn.close()
    money = df[['location','money']]
    a = money[money.money != '面议']

    for index, row in a.iterrows():   # 获取每行的index、row
            #处理城市数据
            sp = row['location'].split('-')
            cp = sp[0].split(',')
            #print(cp[0])
            row['location'] = cp[0]
            #处理薪酬数据
            row['money'] = row['money'].replace('万',"").split('-')
            pp = int(int(row['money'][0])+int(row['money'][1]))/2
            row['money'] = pp

    #全国平均薪酬(元／月)
    avg_all = a.mean(1)/12*10000
    #重新索引
    new_a = a.reindex(range(len(a)),method='ffill')

    list_city = list(new_a['location'])
    Comtype = {}
        # 统计频数
    for item in list_city:
        if item not in Comtype:
            Comtype[item] = 1
        else:
            Comtype[item] += 1

    #统计每个城市的平均薪资
    orderList = list(Comtype.values())
    sort = sorted(Comtype.items(), key=lambda item: item[1], reverse=True)
    city_sort = list(sort)
    city_list1 = dict(city_sort[0:10])


    list_City = list(city_list1.keys())
    city_money = {}
    for i in list_City:
        city_money[i] = 0

    for item in list_City:
        #print(item)
        for i in range(len(list_city)):
            if item == new_a['location'][i]:
                city_money[item] += int(new_a['money'][i])
            else:
                pass

    for item in Comtype:
        if item in city_money:
            city_money[item] = int((city_money[item]/Comtype[item])/12*10000)
    #城市薪资排序，取前10个城市
    return json.dumps(city_money, ensure_ascii=False)


# 统计公司行业分布
# 输出前15的行业
def getComtype():
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    df = pd.read_sql('select * from job_cache;', con=mysql_cn)
    mysql_cn.close()
    comType = df['comIndustry']
    a = list(comType.values)
    Comtype = {}
    # 统计频数
    for item in a:
        if item != "" and item != " ":
            if item not in Comtype:
                Comtype[item] = 1
            else:
                Comtype[item] += 1
        else:
            pass
    sort = sorted(Comtype.items(),key=lambda item:item[1],reverse=True)
    city_sort = list(sort)
    return json.dumps(dict(city_sort[0:15]), ensure_ascii=False)


# 统计学历要求
def getEduNum():
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    df = pd.read_sql('select * from job_cache;', con=mysql_cn)
    mysql_cn.close()
    edu = df['education']
    a = list(edu.values)
    edu_dict = {}
    edu_Num = {}
    # 统计频数
    for item in a:
        if item not in edu_dict:
            edu_dict[item] = 1
        else:
            edu_dict[item] += 1
    edu_Num['本科'] = edu_dict['统招本科'] + edu_dict['本科及以上']
    if "硕士及以上" in edu_dict:
        edu_Num['硕士'] = edu_dict['硕士及以上']
    if '博士' in edu_dict:
        edu_Num['博士'] = edu_dict['博士']
        if "博士后" in edu_dict:
            edu_Num['博士'] = edu_dict['博士'] + edu_dict['博士后']
    edu_Num['学历不限'] = edu_dict['学历不限']
    edu_Num['大专'] = edu_dict['大专及以上']
    return json.dumps(edu_Num, ensure_ascii=False)


# 计算职位的城市分布频数
def getCityNum():
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    df = pd.read_sql('select * from job_cache;', con=mysql_cn)
    mysql_cn.close()
    loca = df['location']
    # 数据预处理，获取城市列表
    city = []
    for i in range(len(loca)):
        sp = loca[i].split('-')
        cp = sp[0].split(',')
        city.append(cp[0])
        #print(city[i])

    city_dict = {}
    # 统计频数
    for item in city:
        if item not in city_dict:
            city_dict[item] = 1
        else:
            city_dict[item] += 1

    # 进行从高到低排序
    orderList = list(city_dict.values())
    sort = sorted(city_dict.items(),key=lambda item:item[1],reverse=True)
    city_sort = list(sort)
    city_list = json.dumps(dict(city_sort[0:10]), ensure_ascii=False)
    return city_list


#求全国或者指定城市的平均薪资
def getCity_Money():
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    df = pd.read_sql('select * from job_cache;', con=mysql_cn)
    mysql_cn.close()
    money = df[['money']]
    a = money[money.money != '面议']
    for index, row in a.iterrows():  # 获取每行的index、row
        # 处理薪酬数据
        row['money'] = row['money'].replace('万', "").split('-')
        pp = int(int(row['money'][0]) + int(row['money'][1])) / 2
        row['money'] = pp
    # 全国平均薪酬(元／月)
    avg_all = a.mean(0) / 12 * 10000
    # print(int(avg_all))
    return str(int(avg_all))


if __name__ == '__main__':
    # 连接MYSQL,获取数据，
    mysql_cn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='wulispider', charset='utf8')
    df = pd.read_sql('select * from job;', con=mysql_cn)
    mysql_cn.close()
    getAvg_Money()

