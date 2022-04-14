#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 09:18:28 2022

@author: qizhishuai
"""

## 导入包
import pandas as pd
import numpy as np
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
    elif freq > 10:
        return 5
    else:
        return 3   

## 会话是否已被提取
def is_extracted(lis) -> list:
    return list(np.zeros_like(lis))

## level1 词
def first_word(string) -> str:
    return string.split()[0]

## level2 词
def second_word(string) -> str:
    return string.split()[1]

## level3 词
def third_word(string) -> str:
    if len(string.split()) < 3:
        return ''
    else:
        return string.split()[2]

## level4 词
def fourth_word(string) -> str:
    if len(string.split()) < 4:
        return ''
    else:
        return string.split()[3]   

## level5 词
def fifth_word(string) -> str:
    if len(string.split()) < 5:
        return ''
    else:
        return string.split()[4]       

## level6 词
def sixth_word(string) -> str:
    if len(string.split()) < 6:
        return ''
    else:
        return string.split()[5]

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
        current = filter_important(sentence)
        res.append(current)
    return res

## 高频词组会话抽取
def process4(string) -> str:
    target = string.split()
    target_str1 = ''.join(target) ## 去除二元组与原会话相同的情况
    target_str2 = ''.join(list(reversed(target)))
    res = ''
    diag_cnt = int(dic1_df[dic1_df['word_list'] == string]['dialogue_cnt'])
    idx = int(dic1_df[dic1_df['word_list'] == string]['index'])
    for i in range(len(data['客户消息分词重要词'])):
        lis = data['客户消息分词重要词'].iloc[i]
        for j in range(len(lis)):
            if is_extracted[i][j] == '':
                current = lis[j]
                diag = data['客户消息原会话'].iloc[i][j]
                contains = True
                for word in target:
                    if word not in current:
                        contains = False
                if contains == True and target_str1 != diag and target_str2 != diag:
                    if diag_cnt > 0:
                        res += diag + '\n'
                        diag_cnt -= 1
                        is_extracted[i][j] = 1
                    else:
                        break
        if diag_cnt == 0:
            print(str(idx) + '(1)') ## 取到diag_cnt数量的会话
            break
    print(str(idx) + '(2)') ## 运行时确认进度
    return res

## 高频词组重新排序
def process5(string) -> str:
    lis = string.split()
    res = ''
    for key in keys:
        for word in lis:
            if key == word:
                res += word + ' '
    return res.strip()      
       
if __name__ == '__main__':
    ## 加载会话数据
    data1 = pd.read_csv('../历史会话_2021年07月01日_2021年09月30日.csv') ## 文件路径
    data2 = pd.read_csv('../历史会话_2021年10月01日_2021年11月30日.csv')
    data3 = pd.read_csv('../历史会话_2021年12月01日_2022年01月17日.csv')
    data4 = pd.read_csv('../历史会话_2022年01月18日_2022年04月02日.csv')
    data = data1.append(data2).append(data3).append(data4)
    data = data[['会话ID', '会话标签', '消息详情']]
    data.reset_index(inplace=True, drop=True)
    
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
    
    data['客户消息分词重要词'] = data['客户消息分词去除停用词'].apply(process3)
    
    dic2 = {}
    for lis in data['客户消息分词重要词']:
        for item in lis:
            current = set()
            for word in item:
                current.add(word)
            if len(current) > 0:
                current = list(current)
                current = sorted(current)
                current = ' '.join(current)
                dic2[current] = dic2.get(current, 0) + 1
    
    dic2 = dict(sorted(dic2.items(), key=lambda x:x[1], reverse=True))
    length = [len(item.split()) for item in list(dic2.keys())] ## 词组长度
    dic2_df = pd.DataFrame(pd.Series(dic2))
    dic2_df['len'] = length
    dic2_df.reset_index(inplace=True)
    dic2_df = dic2_df[dic2_df['len'] > 1] ## 词组长度>1
    dic2_df.reset_index(inplace=True, drop=True)
    dic2_df.columns = ['word_list', 'frequency', 'len']
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
    important_phrases_df = pd.read_excel('../高频词组.xlsx') ## 高频词组
    important_phrases_df = important_phrases_df[important_phrases_df['len'] >= 2]
    important_phrases_df = important_phrases_df[important_phrases_df['frequency'] >= 5]
    important_phrases_df.reset_index(inplace=True)
    important_phrases = important_phrases_df['word_list'].to_list()
    important_phrases_df['dialogue_cnt'] = important_phrases_df['frequency'].apply(dialogue_cnt)  
    data['是否已抽取'] = data['客户消息原会话'].apply(is_extracted)
    is_extracted = list(data['是否已抽取'])
    important_phrases_df['content'] = important_phrases_df['word_list'].apply(process4)
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
    
    diag_id_list = []
    diag_content_list = []
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

    for i in range(len(data1['客户消息分词去除停用词'])):
        sensitive_contains = False
        for j in range(len(data1['客户消息分词去除停用词'][i])):
            current = data1['客户消息分词去除停用词'][i][j]
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
                sensitive_contains = True
        if sensitive_contains == True:
            for j in range(len(data1['客户消息分词去除停用词'][i])):
                current = data1['客户消息分词去除停用词'][i][j]
                diag_id_list.append(data1['会话ID'][i])
                diag_content_list.append(data1['客户消息原会话'][i][j])
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
        else:
            continue
    
    dic4 = {
    '会话id': diag_id_list,
    '原会话': diag_content_list,
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
    
    ## 高频词组词频
    dic5 = {}
    for i in range(len(important_phrases)):
        for word in important_phrases[i].split():
            dic5[word] = dic5.get(word, 0) + 1
    dic5 = dict(sorted(dic5.items(), key=lambda x:x[1], reverse=True))
    dic5_df = pd.DataFrame(pd.Series(dic5)).reset_index()
    dic5_df.to_excel('../高频词组中词频排序.xlsx')

    ##高频词组按词频重新排序
    keys = list(dic5.keys())
    important_phrases_df['sorted_word_list'] = important_phrases_df['word_list'].apply(process5)
    
    ## 高频词组结构化
    important_phrases_df_2 = important_phrases_df[important_phrases_df['len'] == 2] 
    important_phrases_df_3 = important_phrases_df[important_phrases_df['len'] == 3] 
    important_phrases_df_4 = important_phrases_df[important_phrases_df['len'] == 4] 
    important_phrases_df_5 = important_phrases_df[important_phrases_df['len'] == 5] 
    important_phrases_df_6 = important_phrases_df[important_phrases_df['len'] == 6]       

    word_list = []
    frequency = []
    length = []
    is_selected3 = [0 for i in range(len(important_phrases_df_3))]
    is_selected4 = [0 for i in range(len(important_phrases_df_4))]
    is_selected5 = [0 for i in range(len(important_phrases_df_5))]
    is_selected6 = [0 for i in range(len(important_phrases_df_6))]     
    
    for i in range(len(important_phrases_df_2)):
        wl2 = important_phrases_df_2.iloc[i]['sorted_word_list']
        wl2_list = wl2.split()
        freq2 = important_phrases_df_2.iloc[i]['frequency']
        len2 = important_phrases_df_2.iloc[i]['len']
        word_list.append(wl2)
        frequency.append(freq2)
        length.append(len2)
        for j in range(len(important_phrases_df_3)):
            wl3 = important_phrases_df_3.iloc[j]['sorted_word_list']
            wl3_list = wl3.split()
            if wl3_list[:2] == wl2_list and is_selected3[j] == 0:
                is_selected3[j] = 1
                freq3 = important_phrases_df_3.iloc[j]['frequency']
                len3 = important_phrases_df_3.iloc[j]['len']
                word_list.append(wl3)
                frequency.append(freq3)
                length.append(len3)
                for k in range(len(important_phrases_df_4)):
                    wl4 = important_phrases_df_4.iloc[k]['sorted_word_list']
                    wl4_list = wl4.split()
                    if wl4_list[:3] == wl3_list and is_selected4[k] == 0:
                        is_selected4[k] = 1
                        freq4 = important_phrases_df_4.iloc[k]['frequency']
                        len4 = important_phrases_df_4.iloc[k]['len']
                        word_list.append(wl4)
                        frequency.append(freq4)
                        length.append(len4)
                        for m in range(len(important_phrases_df_5)):
                            wl5 = important_phrases_df_5.iloc[m]['sorted_word_list']
                            wl5_list = wl5.split()
                            if wl5_list[:4] == wl4_list and is_selected5[m]  == 0:
                                is_selected5[m] = 1
                                freq5 = important_phrases_df_5.iloc[m]['frequency']
                                len5 = important_phrases_df_5.iloc[m]['len']
                                word_list.append(wl5)
                                frequency.append(freq5)
                                length.append(len5)
                                for n in range(len(important_phrases_df_6)):
                                    wl6 = important_phrases_df_6.iloc[n]['sorted_word_list']
                                    wl6_list = wl6.split()
                                    if wl6_list[:5] == wl5_list and is_selected6[n] == 0:
                                        is_selected6[n] = 1
                                        freq6 = important_phrases_df_6.iloc[n]['frequency']
                                        len6 = important_phrases_df_6.iloc[n]['len']
                                        word_list.append(wl6)
                                        frequency.append(freq6)
                                        length.append(len6)
        print(i+1) ## 运行时确认进度
        
    for idx, value in enumerate(is_selected3): ## 未结构化的词组放在末尾
        if value == 0:
            word_list.append(important_phrases_df_3.iloc[idx]['sorted_word_list'])
            frequency.append(important_phrases_df_3.iloc[idx]['frequency'])
            length.append(important_phrases_df_3.iloc[idx]['len'])
    
    for idx, value in enumerate(is_selected4):
        if value == 0:
            word_list.append(important_phrases_df_4.iloc[idx]['sorted_word_list'])
            frequency.append(important_phrases_df_4.iloc[idx]['frequency'])
            length.append(important_phrases_df_4.iloc[idx]['len'])
    
    for idx, value in enumerate(is_selected5):
        if value == 0:
            word_list.append(important_phrases_df_5.iloc[idx]['sorted_word_list'])
            frequency.append(important_phrases_df_5.iloc[idx]['frequency'])
            length.append(important_phrases_df_5.iloc[idx]['len'])
            
    for idx, value in enumerate(is_selected6):
        if value == 0:
            word_list.append(important_phrases_df_6.iloc[idx]['sorted_word_list'])
            frequency.append(important_phrases_df_6.iloc[idx]['frequency'])
            length.append(important_phrases_df_6.iloc[idx]['len'])

    dic6 = {
    'word_list': word_list,
    'frequency': frequency,
    'length': length
    }
    dic6_df = pd.DataFrame(dic6) 
    dic6_df['level1'] = dic6_df['word_list'].apply(first_word)
    dic6_df['level2'] = dic6_df['word_list'].apply(second_word)
    dic6_df['level3'] = dic6_df['word_list'].apply(third_word)
    dic6_df['level4'] = dic6_df['word_list'].apply(fourth_word)
    dic6_df['level5'] = dic6_df['word_list'].apply(fifth_word)
    dic6_df['level6'] = dic6_df['word_list'].apply(sixth_word)    
    dic6_df.to_excel('../高频词组结构化.xlsx')

    ## 结构化高频词组抽取原会话
    dic6_df['dialogue_cnt'] = dic6_df['frequency'].apply(dialogue_cnt) 
    data['是否已抽取'] = data['客户消息原会话'].apply(is_extracted)
    is_extracted = list(data['是否已抽取'])
    dic6_df['content'] =  dic6_df['word_list'].apply(process4) 
    dic6_df.to_excel('../高频词组结构化抽取原会话.xlsx')
