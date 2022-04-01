#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 09:18:28 2022

@author: qizhishuai
"""

## 导入包
import pandas as pd
import re
import jieba

## 数据处理

## 筛选客户消息
def start_with_alpha_or_digit(string) -> bool:
    return (ord(string[0]) >= 48 and ord(string[0]) <= 57) or (ord(string[0]) >= 65 and ord(string[0]) <= 90) or (ord(string[0]) >= 97 and ord(string[0]) <= 122)

## 提取中文
def find_chinese(string) -> str:
    return ''.join(re.findall(r'[\u4e00-\u9fa5]', string))

## 分词
def segment(string) -> list:
    return jieba.lcut(string)

## 去除停用词
def remove_stopwords(str_list) -> list:
    res = []
    for word in str_list:
        if word not in stopwords and len(word) >= 2:
            res.append(word)
    return res

## 筛选重要词
def filter_important(str_list) -> list:
    res = []
    for word in str_list:
        if word in important_words:
            res.append(word)
    return res
    
## 提取客户原会话
def process1(string) -> list:
    res = []
    for line in str(string).split('\n'):
        if len(line) > 0 and start_with_alpha_or_digit(line):
            current = find_chinese(line)
            if len(current) > 0:
                res.append(current)
    return res

## 客户会话分词去除停用词
def process2(str_list) -> list:
    res = []
    for sentence in str_list:
        current = segment(sentence)
        current = remove_stopwords(current)
        res.append(current)
    return res

## 客户会话分词重要词
def process3(str_list) -> list:
    res = []
    for sentence in str_list:
        current = segment(sentence)
        current = filter_important(current)
        res.append(current)
    return res

if __name__ == '__main__':
    ## 加载会话数据
    data1 = pd.read_csv('../历史会话_2021年07月01日_2021年09月30日.csv') ## 文件路径
    data2 = pd.read_csv('../历史会话_2021年10月01日_2021年11月30日.csv')
    data3 = pd.read_csv('../历史会话_2021年12月01日_2022年01月17日.csv')
    data = data1.append(data2).append(data3)
    data = data[['会话ID', '会话标签', '消息详情']]
    
    ## 停用词表
    stopwords = [line.strip() for line in open('../stopwords.txt', encoding='UTF-8').readlines()]
    
    data['客户消息原会话'] = data['消息详情'].apply(process1)
    data['客户消息分词去除停用词'] = data['客户消息原会话'].apply(process2)
    
    ## 高频词 
    dic1 = {}
    for lis in data['客户消息分词去除停用词']:
        for item in lis:
            for word in item:
                dic1[word] = dic1.get(word, 0) + 1
    
    dic1 = dict(sorted(dic1.items(), key=lambda x:x[1], reverse=True)) ## 按词频排序
    dic1_df = pd.DataFrame(pd.Series(dic1))
    dic1_df.to_excel('../高频词.xlsx') ## 输出高频词文档
    
    ## 高频词组
    important_words_df = pd.read_excel('../筛选后的高频词.xlsx')
    important_words = important_words_df['word'].to_list()
    
    data['客户消息分词重要词'] = data['客户消息原会话'].apply(process3)
    
    dic2 = {}
    for lis in data['客户消息分词重要词']:
        for item in lis:
            current = set()
            for word in item:
                current.add(word)
            if len(current) > 0:
                current = ' '.join(current)
                dic2[current] = dic2.get(current, 0) + 1
    
    dic2 = dict(sorted(dic2.items(), key=lambda x:x[1], reverse=True))
    length = [len(item.split()) for item in list(dic2.keys())] ## 词组长度
    dic2_df = pd.DataFrame(pd.Series(dic2))
    dic2_df['len'] = length
    dic2_df.reset_index(inplace=True)
    dic2_df = dic2_df[dic2_df['len'] > 1] ## 词组长度>1
    dic2_df.to_excel('../高频词组.xlsx')                 
    
    ## 连接词数
    word_set = [set() for i in range(len(important_words))]
    dic3 = dict(zip(important_words, word_set))
    for lis in data['客户消息分词重要词']:
        for item in lis:
            for idx, word in enumerate(item):
                connected_words = item[: idx] + item[idx + 1:]
                for other_word in connected_words:
                    dic3[word].add(other_word)
    connected_num = [len(item) for item in list(dic3.values())]
    dic3_df = pd.DataFrame(pd.Series(dic3))
    dic3_df['连接数'] = connected_num
    dic3_df.reset_index(inplace=True)
    dic3_df = dic3_df.sort_values(by='连接数', ascending=False)
    dic3_df.to_excel('../高频词连接数.xlsx') 

    
                