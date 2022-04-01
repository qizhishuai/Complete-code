#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 17:14:29 2022

@author: qizhishuai
"""

import pandas as pd
import re
import jieba

def start_with_G(string) -> bool:
    return string[0] == 'G'

def find_chinese(string) -> str:
    return ''.join(re.findall(r'[\u4e00-\u9fa5]', string))

def segment(string) -> list:
    return jieba.lcut(string)

def remove_stopwords(str_list) -> list:
    res = []
    for word in str_list:
        if word not in stopwords and len(word) >= 2:
            res.append(word)
    return res

def process2(str_list) -> list:
    res = []
    for sentence in str_list:
        current = segment(sentence)
        current = remove_stopwords(current)
        res.append(current)
    return res

def process4(string) -> list:
    res = []
    str_list = str(string).split('\n')
    for i in range(len(str_list) - 1):
        if len(str_list[i]) > 0:
            if start_with_G(str_list[i]):
                current = find_chinese(str_list[i + 1])
                if len(current) > 0:
                    res.append(current)
    return res

if __name__ == '__main__':
    data1 = pd.read_excel('../history-1648784056528-659dedf2-73fd-4dd2-9cca-2674cf6d68f3.xls') 
    data2 = pd.read_excel('../history-1648784185307-dc641917-2f44-421f-8423-27f1bd1c09f2.xls')
    data3 = pd.read_excel('../history-1648784312676-6a20c9f6-5221-4918-ab13-33051f3492ce.xls')
    data4 = pd.read_excel('../history-1648784338027-f15f1012-7334-4a14-a05c-81289d030b71.xls')
    data = data1.append(data2).append(data3).append(data4)
    data = data[['会话ID', '会话内容']]
    
    stopwords = [line.strip() for line in open('../stopwords.txt', encoding='UTF-8').readlines()]
    
    data['客户消息原会话'] = data['会话内容'].apply(process4)
    data['客户消息分词去除停用词'] = data['客户消息原会话'].apply(process2)
    
    dic = {}
    for lis in data['客户消息分词去除停用词']:
        for item in lis:
            for word in item:
                dic[word] = dic.get(word, 0) + 1
    
    dic = dict(sorted(dic.items(), key=lambda x:x[1], reverse=True)) ## 按词频排序
    dic_df = pd.DataFrame(pd.Series(dic))
    dic_df.to_excel('../高频词.xlsx') 