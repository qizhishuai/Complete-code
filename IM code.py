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

## 抽取客户会话数量
def dialogue_cnt(freq) -> int:
    if freq > 500:
        return 50
    elif freq > 100:
        return 30
    elif freq > 50:
        return 20
    elif freq > 20:
        return 10
    else:
        return 5   

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

## 高频词组会话抽取
def process4(string) -> str:
    target = string.split()
    diag_cnt = int(important_phrases_df[important_phrases_df['phrase'] == string]['dialogue_cnt'])
    res = ''
    for i in range(len(data['客户消息分词重要词'])):
        lis = data['客户消息分词重要词'][i]
        for j in range(len(lis)):
            words = lis[j]
            not_contains = False
            for item in target:
                if item not in words:
                    not_contains = True
            if not_contains == False:
                diag_cnt -= 1
                if diag_cnt > 0:
                    res.append(data['客户消息原会话'][i][j])
                else:
                    break
        if diag_cnt == 0:
            break
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

    ## 根据高频词组抽取客户会话
    important_phrases_df = pd.read_excel('../筛选后的高频词组.xlsx') ## 筛过后的高频词组文件
    important_phrases = important_phrases_df['phrase'].to_list()
    important_phrases_df['dialogue_cnt'] = important_phrases_df['frequency'].apply(dialogue_cnt)
    important_phrases_df['content'] = important_phrases_df['phrase'].apply(process4)
    important_phrases_df.to_excel('../高频词组会话内容.xlsx')
    
    ## 根据词性标注表提取原会话
    labels_df = pd.read_excel('../词性标注.xlsx')
    
    xiangguan = labels_df[labels_df['是否业务相关'] == 1]['词频>50，中文'].to_list()
    mingan = labels_df[labels_df['敏感词'] == 1]['词频>50，中文'].to_list()
    qingxu = labels_df[labels_df['情绪词'] == 1]['词频>50，中文'].to_list()
    tianqi = labels_df[labels_df['天气词汇'] == 1]['词频>50，中文'].to_list()
    xingche = labels_df[labels_df['行车或所在场景词'] == 1]['词频>50，中文'].to_list()
    changjia = labels_df[labels_df['厂家行为词'] == 1]['词频>50，中文'].to_list()
    yonghu = labels_df[labels_df['用户行为词'] == 1]['词频>50，中文'].to_list()
    shijian = labels_df[labels_df['时间'] == 1]['词频>50，中文'].to_list()
    dili = labels_df[labels_df['地理信息'] == 1]['词频>50，中文'].to_list()
    duixiang = labels_df[labels_df['对象\n人/物/指标'] == 1]['词频>50，中文'].to_list()
    xianxiang = labels_df[labels_df['现象描述'] == 1]['词频>50，中文'].to_list()
    
    diag_list = []
    xiangguan_list = []
    mingan_list = []
    qingxu_list = []
    tianqi_list = []
    xingche_list = []
    changjia_list = []
    yonghu_list = []
    shijian_list = []
    dili_list = []
    duixiang_list = []
    xianxiang_list = []
    
    for i in range(len(data['客户消息分词去除停用词'])):
        for j in range(len(data['客户消息分词去除停用词'][i])):
            current = data['客户消息分词去除停用词'][i][j]
            lis = []
            xiangguan_contains = False
            mingan_contains = False
            qingxu_contains = False
            for word in current:
                if word in xiangguan:
                    xiangguan_contains = True
                if word in mingan:
                    mingan_contains = True
                if word in qingxu:
                    qingxu_contains = True
            if xiangguan_contains == True and (mingan_contains == True or qingxu_contains == True):
                diag_list.append(data['客户消息原会话'][i][j])
                xiangguan_list.append('')
                mingan_list.append('')
                qingxu_list.append('')
                tianqi_list.append('')
                xingche_list.append('')
                changjia_list.append('')
                yonghu_list.append('')
                shijian_list.append('')
                dili_list.append('')
                duixiang_list.append('')
                xianxiang_list.append('')
                for word in current:
                    if word in xiangguan:
                        xiangguan_list[-1] += word + ' '
                    if word in mingan:
                        mingan_list[-1] += word + ' '
                    if word in qingxu:
                        qingxu_list[-1] += word + ' '
                    if word in tianqi:
                        tianqi_list[-1] += word + ' '
                    if word in xingche:
                        xingche_list[-1] += word + ' '
                    if word in changjia:
                        changjia_list[-1] += word + ' '
                    if word in yonghu:
                        yonghu_list[-1] += word + ' '
                    if word in shijian:
                        shijian_list[-1] += word + ' '
                    if word in dili:
                        dili_list[-1] += word + ' '
                    if word in duixiang:
                        duixiang_list[-1] += word + ' '
                    if word in xianxiang:
                        xianxiang_list[-1] += word + ' '
    dic4 = {
    '原会话': diag_list,
    '业务相关词': xiangguan_list,
    '敏感词': mingan_list,
    '情绪词': qingxu_list,
    '天气词': tianqi_list,
    '行车或所在场景词': xingche_list,
    '厂家行为词': changjia_list,
    '用户行为词': yonghu_list,
    '时间': shijian_list,
    '地理信息': dili_list,
    '对象': duixiang_list,
    '现象描述': xianxiang_list
    }
    
    dic4_df = pd.DataFrame(dic4)
    dic4_df.to_excel('../标注词性.xlsx') 
    
