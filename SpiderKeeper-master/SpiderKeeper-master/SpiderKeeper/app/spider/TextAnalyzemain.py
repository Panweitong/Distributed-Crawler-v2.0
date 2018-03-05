#-*- encoding:utf-8 -*-
from __future__ import print_function
import sys
from SpiderKeeper.app.spider import TextRank4Keyword, TextRank4Sentence

try:
    #reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

import codecs



def TextAnalyze1(text):
    tr4w = TextRank4Keyword.TextRank4Keyword()
    tr4w.analyze(text=text, lower=True, window=2)   # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象
    # print( '关键词：' )
    result=[]
    for item in tr4w.get_keywords(10, word_min_len=2):
         result.append(item.word+'&nbsp; &nbsp;')
    return result
    # result = tr4w.get_keywords(10, word_min_len=1)   #返回的数据
    # print(result.word)


def TextAnalyze2(text):
    tr4s = TextRank4Sentence.TextRank4Sentence()
    tr4s.analyze(text=text, lower=True, source = 'all_filters')
    # print()
    # print( '摘要：' )
    result = []
    for item in tr4s.get_key_sentences(num=1):
        result.append(item.sentence)
        # print(result)
    return result
    # result1 = tr4s.get_key_sentences(num=1)   #返回的数据
    # print(result1)

# if __name__ == '__main__':
#     TextAnalyze1("中新网北京12月1日电(记者 张曦) 30日晚，高圆圆和赵又廷在京举行答谢宴，诸多明星现身捧场，其中包括张杰(微博)、谢娜(微博)夫妇、何炅(微博)、蔡康永(微博)、徐克、张凯丽、黄轩(微博)")