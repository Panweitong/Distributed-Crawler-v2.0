#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import psutil
import MySQLdb as mdb
import time


def create_db():
    # 连接
    db = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
    db.autocommit(True)
    c = db.cursor()

    # 创建表
    # 删除旧表，如果存在（因为这是临时数据）
    c.execute("DROP TABLE IF EXISTS cpu")
    c.execute('''CREATE TABLE `cpu`(`id` INTEGER unsigned NOT NULL AUTO_INCREMENT,`insert_time` text DEFAULT NULL,`cpu1` float DEFAULT NULL,
  `cpu2` float DEFAULT NULL,
  `cpu3` float DEFAULT NULL,
  `cpu4` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8 ''')

    # 关闭
    c.close()
    db.close()


def save_to_db(data1, data2, data3, data4, data5):
    '''参数data格式：['00:01',3.5, 5.9, 0.7, 29.6]'''
    # 建立连接
    db = mdb.connect(host="127.0.0.1", port=3306,user="root", passwd="123456",db="wulispider", charset="utf8")
    db.autocommit(True)
    c = db.cursor()

    sql="INSERT INTO cpu(insert_time,cpu1,cpu2,cpu3,cpu4) VALUES ('%s', '%f', '%f', '%f', '%f')" % (data1, data2, data3, data4, data5)
    # 插入数据
    c.execute(sql)

    # 提交！！！
    db.commit()

    # 关闭连接
    db.close()


# 创建表
create_db()

# 通过循环，对系统进行监控
while True:
    # 获取系统cpu使用率（每隔1秒）
    cpus = psutil.cpu_percent(interval=3, percpu=True)

    # 获取系统时间（只取分:秒）
    t = time.strftime('%H:%M:%S', time.localtime())

    # 保存到数据库
    save_to_db(t, cpus[0], cpus[1], cpus[2], cpus[3])
    print('save a data')