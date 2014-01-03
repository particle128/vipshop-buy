# coding=utf-8

import re
import time
from selenium import webdriver 
from config_local import *
import platfm
import proc 

def auto_pick(driver,sizeIdx,dts):
	'''全自动模式'''
	for dl in driver.find_elements_by_class_name('J_pro_items'):
		try:
			title = dl.find_element_by_class_name('pro_list_tit').text
			print 'test',title
			if (not filter(lambda x:x in title,Excepts) and 
				(Keywords and filter(lambda x:x in title,Keywords) == Keywords or not Keywords)):
				price = dl.find_element_by_tag_name("em").text.lstrip(u'¥')
				discount = dl.find_element_by_xpath("./dd[@class='pro_list_data']/span").text
				discount = re.search(r'\((.*)\)',discount).group(1).rstrip(u'折')
				print 'price=',price,'discount=',discount
				if (float(PriceSpan[0]) <= float(price) <= float(PriceSpan[1]) and 
					float(DisSpan[0]) <= float(discount) <= float(DisSpan[1])):
					print 'pick it'
					href = (dl.find_element_by_tag_name('a').get_attribute('href')
						+' ' + sizeIdx+platfm.Line)
					proc.send_to_subp(href)
		except Exception as e: #忽略可能出现的StaleElementReferenceException错误
			print e
