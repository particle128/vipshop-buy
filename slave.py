#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function #必须要出现在文件开头
from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import sys
import re
from config import *
import os

MaxReload=2 #reload的最大次数
HasGood=False
TimeoutCnt=0 #超时计数

def p_print(*args):
	'带有pid的输出'
	print(os.getpid(),':',end='')
	for arg in args:
		print(arg,end=' ')
	print('\n',end='')

def buy(driver,size):
	"购买对应尺码的商品"
	p_print('buy')
	SizeReg=''
	if size!=u'默认':
		SizeReg=u'^'+size+u'([^.]|$)'
	else: #如果是默认尺码，那就所有商品都选
		SizeReg=u'.*'
	cnt=0
	ref=False
	while True:
		try:
			if ref:
				driver.refresh()
			# 用xpath定位element
			ul=driver.find_element_by_xpath("//table[@class='tab_data']/tbody/tr/td/div/div/ul")
			btn=driver.find_element_by_id('J_cartAdd_submit')
			for li in ul.find_elements_by_tag_name('li'):
				span=li.find_element_by_tag_name('span')
				# 没有售完，且大小符合要求
				if 'normal' in span.get_attribute('class') and re.search(SizeReg,span.text.strip('" ')):
				#if 'normal' in span.get_attribute('class') and span.text.strip('" ') in Size:
					action=ActionChains(driver)
					action.click(li).click(btn).perform() # ！！！ click会超时，至少2s的page_load_timeout
					p_print('got size',span.text.strip())
					global HasGood #!!!全局变量
					HasGood=True
					time.sleep(1)
		except TimeoutException:
			p_print('timeout')
			ref=False
		except Exception as e:
			p_print(e)
			global TimeoutCnt
			TimeoutCnt+=1
			if cnt==MaxReload:
				p_print('get to MaxReload,return')
				return #直接函数返回，忽略该商品
			else:
				cnt+=1
				cur=(cnt+1)*BuyTimeout
				driver.set_page_load_timeout(cur) #每次超时时间，延长BuyTimeout
				p_print(cur)
				ref=True#重新加载该页
		else:
			break

def login(driver,user,pwd):
	driver.get(LoginUrl)
	driver.find_element_by_id("J_L_name").send_keys(user)
	driver.find_element_by_id('J_L_psw').send_keys(pwd)
	driver.find_element_by_id("user_login_form").submit()
	driver.back()#!!!
	

if __name__=='__main__':

	p_print('slave')
	user,pwd,xpos=sys.argv[1],sys.argv[2],sys.argv[3]
	p_print(user,pwd)
	while True: #防止调用Chrome出错
		try:
			driver=webdriver.Chrome()
		except:
			time.sleep(2)
		else:
			break
	
	driver.set_window_size(ScreenW/len(Account),ScreenH2)
	driver.set_window_position(int(xpos),ScreenH1)
	login(driver,user,pwd)

	try:
		driver.set_page_load_timeout(BuyTimeout) #从配置文件读取timeout值
		while True:
			#select([sys.stdin],[],[])
			infos=sys.stdin.readline() #!!!read()不行
			#退出
			if infos.find('q')==0: #开头是q的，表示退出
				if TimeoutCnt>=2:#发生两次超时
					timeout_inc(0.5)
				if HasGood:
					p_print('has goods')
					driver.maximize_window() #最大化有物品的窗口
					#停止
					while True:
						time.sleep(10000)
				else:
					p_print('has no goods')
					break
			href=infos.split()[0]
			sizeIdx=int(infos.split()[1])
			size=Size[sizeIdx]
			p_print(href,size)
			try:
				driver.get(href)
			except TimeoutException:
				pass
			buy(driver,size)
	except Exception as e:
		p_print('error:',e)
	finally:
		driver.quit()
		p_print('subprocess exits')



