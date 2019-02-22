# -*- encoding:utf-8 -*-
"""
 * Copyright (C) 2017 OwnThink.
 *
 * Name        : findword.py - 新词发现
 * Author      : Yener <yener@ownthink.com>
 * Version     : 0.01
 * Description : 新词发现算法实现
 special thanks to 
 http://blog.csdn.net/xiaokang06/article/details/50616983
 https://github.com/zoulala/New_words_find
"""
import re
import sys
from math import log
from collections import Counter


max_word_len = 6
re_chinese = re.compile(u"[\w]+", re.U)

def count_words(input):
	word_freq = Counter()
	fin = open(input, 'r', encoding='utf8')
	for index, line in enumerate(fin):
		words = []
		for sentence in re_chinese.findall(line):
			length = len(sentence)
			for i in range(length):
				words += [sentence[i: j + i] for j in range(1, min(length - i+1, max_word_len + 1))]
		word_freq.update(words)
	fin.close()
	return word_freq
	
def lrg_info(word_freq, total_word, min_freq, min_mtro):
	l_dict = {}
	r_dict = {}
	k = 0
	for word, freq in word_freq.items():
		k += 1
		if len(word) < 3: 
			continue
			
		left_word = word[:-1]
		ml = word_freq[left_word]
		if ml > min_freq:
			mul_info1 = ml * total_word / (word_freq[left_word[1:]] * word_freq[left_word[0]])
			mul_info2 = ml * total_word / (word_freq[left_word[-1]] * word_freq[left_word[:-1]])
			mul_info = min(mul_info1, mul_info2)
			
			if mul_info > min_mtro:
				if left_word in l_dict:
					l_dict[left_word].append(freq)
				else:
					l_dict[left_word] = [ml, freq]

		right_word = word[1:]
		mr = word_freq[right_word]
		if mr > min_freq:
			mul_info1 = mr * total_word / (word_freq[right_word[1:]] * word_freq[right_word[0]])
			mul_info2 = mr * total_word / (word_freq[right_word[-1]] * word_freq[right_word[:-1]])
			mul_info = min(mul_info1, mul_info2)
			
			if mul_info > min_mtro:     
				if right_word in r_dict:
					r_dict[right_word].append(freq)
				else:
					r_dict[right_word] = [mr, freq]   
	return l_dict, r_dict
 
def cal_entro(r_dict):
	entro_r_dict = {}
	for word in r_dict:
		m_list = r_dict[word]

		r_list = m_list[1:]
		fm = m_list[0]

		entro_r = 0
		krm = fm - sum(r_list)
		if krm > 0:
			entro_r -= 1 / fm * log(1 / fm, 2) * krm

		for rm in r_list:
			entro_r -= rm / fm * log(rm / fm, 2)
		entro_r_dict[word] = entro_r
		
	return entro_r_dict
	  
def entro_lr_fusion(entro_r_dict,entro_l_dict):
	entro_in_rl_dict = {}
	entro_in_r_dict = {}
	entro_in_l_dict =  entro_l_dict.copy()
	for word in entro_r_dict:
		if word in entro_l_dict:
			entro_in_rl_dict[word] = [entro_l_dict[word], entro_r_dict[word]]
			entro_in_l_dict.pop(word)
		else:
			entro_in_r_dict[word]  = entro_r_dict[word]
	return entro_in_rl_dict,entro_in_l_dict,entro_in_r_dict
   
def entro_filter(entro_in_rl_dict,entro_in_l_dict,entro_in_r_dict,word_freq,min_entro):
	entro_dict = {}
	l, r, rl = 0, 0, 0
	for word in entro_in_rl_dict:
		if entro_in_rl_dict[word][0]>min_entro and entro_in_rl_dict[word][1]>min_entro:
			entro_dict[word] = word_freq[word]
			rl +=1

	for word in entro_in_l_dict:
		if entro_in_l_dict[word] > min_entro:
			entro_dict[word] = word_freq[word]
			l += 1

	for word in entro_in_r_dict:
		if entro_in_r_dict[word] > min_entro:
			entro_dict[word] = word_freq[word]
			r += 1

	return entro_dict

	
def new_word_find(input, output):
	min_freq = 10
	min_mtro = 80
	min_entro = 3
	
	word_freq = count_words(input)  
	total_word = sum(word_freq.values())
	
	l_dict, r_dict = lrg_info(word_freq, total_word, min_freq, min_mtro)

	entro_r_dict = cal_entro(l_dict)
	entro_l_dict = cal_entro(r_dict)
	del l_dict,r_dict

	entro_in_rl_dict,entro_in_l_dict,entro_in_r_dict = entro_lr_fusion(entro_r_dict,entro_l_dict)
	del entro_r_dict,entro_l_dict

	entro_dict = entro_filter(entro_in_rl_dict,entro_in_l_dict,entro_in_r_dict,word_freq,min_entro)
	del entro_in_rl_dict,entro_in_l_dict,entro_in_r_dict,word_freq

	result = sorted(entro_dict.items(), key=lambda x:x[1], reverse=True)

	with open(output, 'w',encoding='utf-8') as kf:
		for w, m in result:
			kf.write(w + '\t%d\n' % m)
 
if __name__ == "__main__":
	input = 'test_msr.txt'
	output = 'count.txt'
	new_word_find(input, output)
	
