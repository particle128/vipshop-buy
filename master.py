#!/usr/bin/env python
# coding=utf-8

import re
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from config_local import *
import platfm
import proc
import page
import auto
import term


MixFlag = False  # 混合模式
Depth=1  # 页面的嵌套深度

def control(driver,sizeIdx):
	'''在一页上处理用户按键'''
	dts=driver.find_elements_by_class_name('pro_list_pic')
	platfm.roll_down(driver,dts)

	if AutoPickMode:
		auto.auto_pick(driver,sizeIdx,dts)
	else:
		term.own_pick(driver,sizeIdx,dts)

def nest_page(driver):
	'''处理嵌套页面的情况：页面内又含有分支页面'''
	global Depth
	if Depth<=1: #深度最多为1层
		try:
			driver.find_element_by_class_name('pro_list_pic')
		except NoSuchElementException:
			Depth+=1
			print 'need to jump again'
			eles=driver.find_elements_by_tag_name('a')
			pattern=re.compile('show-\d+.html$')
			for ele in eles:
				if pattern.search(str(ele.get_attribute('href'))):
					print 'before click'
					action=ActionChains(driver)
					action.click(ele).perform()
					print 'after click'
					# 切换到新的窗口
					base_page=ele.get_attribute('href')
					print 'go into '+ base_page
					try:
						driver.current_url
					except:
						pass
					page.switch_do(driver,process,(base_page,))
			Depth-=1
			return 

def process(driver,base_page):
	'''处理每一个品牌'''
	nest_page(driver) #嵌套页面

	sizeIdx=-1
	for type,size in zip(Type,Size):
		print type,size
		has_more=True
		num=1
		sizeIdx+=1
		while has_more:
			# 加载新页
			new_url=base_page+"?q=0|%s|%s|%s|%s|%d"%(TYPE[type],SIZE[size.lower()],EMPTY[Empty],SORT[Sort],num)
			print new_url
			driver.set_page_load_timeout(3) #3s超时
			page.call_ignore(driver.get,new_url)
			num+=1
			# 判断是否存在
			try: 
				driver.find_element_by_class_name('pro_find_none')
			except NoSuchElementException:
				pass
			else: 
				print platfm.local_str('不存在该类别的商品')
				break 
			# 判断是否是最后一页
			try:
				attr=driver.find_element_by_class_name('page_next').get_attribute('href')
				if not attr:
					has_more=False
			except:
				has_more=False

			control(driver,str(sizeIdx))


def search_brand(item,name):
	'''搜需要的品牌'''
	try: #如果找不到，就直接return
		lis=driver.find_elements_by_class_name(item)
	except:
		print platfm.local_str('没有'+item+'条目，返回')
		return
	#driver.set_page_load_timeout(0.5) #0.5s超时,太短的话(0.1s)click可能会超时
	driver.set_page_load_timeout(4) #等待嵌套页面加载需要的时间较长
	for li in lis:
		info=li.find_element_by_class_name(name).text
		print info
		# 至少包括Brands里的一项，包括Keys里的所有项
		if (filter(lambda x: x.lower() in info.lower(),Brands) and 
			(Keys and Keys==filter(lambda x:x.lower() in info.lower(),Keys) or not Keys )):
			if u"男女" in info:
				MixFlag=True
			print 'before click'
			action=ActionChains(driver)
			action.click(li).perform()
			print 'after click'
			time.sleep(0.5)
			# 切换到新的窗口
			base_page=''
			try:
				base_page=driver.current_url
			except:
				pass
			print 'go into '+info+base_page
			page.switch_do(driver,process,(base_page,))
			MixFlag=False



if __name__=='__main__':
	try:
		platfm.init()
		proc.forks()
		print 'after forks'
	
		driver=webdriver.Chrome()
		driver.set_window_position(0,0)
		driver.set_window_size(ScreenW,ScreenH1)

		platfm.first_timeout(driver)
		page.call_ignore(driver.get,HomeUrl)

		if TestMode:
			# 如果不执行wait_for_begin，就必须刷新一次，否则选地址的div挡着没法点击链接
			print 'TestMode'
			# ele=WebDriverWait(driver,60,2,(Exception))
			# .until(lambda x:x.find_element_by_class_name('sdf_item'))
			driver.set_page_load_timeout(40)#40s超时,等待第一次加载
			page.call_ignore(driver.refresh)
		else:
			print 'Non-TestMode'
			page.wait_for_begin(driver)

		print 'after wait_for_begin'

		# 展示区
		search_brand('sdf_item','sdf_name') #class='sdf_item sdf_item_only'也包括在内
		# 今日新品
		search_brand('s_mod','s_info_name')
	except Exception as e:
		print e
	finally:
		driver.quit()
		proc.inform_subp()
		platfm.uninit()


