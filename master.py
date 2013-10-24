#!/usr/bin/env python
# coding=utf-8

import selenium
from selenium import webdriver 
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import subprocess
import sys
import re
from urlparse import urlparse
import sys
import platform
from config import *

IsWindows=False
Line=''
if platform.system()=="Windows":
	import msvcrt
	IsWindows=True
	Line='\r\n'
else: #Linux
	import termios
	#from select import select
	Line='\n'


MixFlag=False #混合模式
ps=[] #子进程列表
Depth=1 #页面的嵌套深度

def local_str(s):
	if IsWindows:
		if isinstance(str,unicode):
			return s.encode('gbk')
		else:
			return s.decode('utf-8').encode('gbk')
	else:
		return s

def forks():
	'创建多个进程'
	xpos=0
	for user,pwd in Account:
		if IsWindows:
			ps.append(subprocess.Popen(['slave.exe',user,pwd,str(xpos)],stdin=subprocess.PIPE)) 
		else:
			ps.append(subprocess.Popen(['python','slave.py',user,pwd,str(xpos)],stdin=subprocess.PIPE)) 
		print user,pwd,xpos,'slave.py'
		xpos+=ScreenW/len(Account)

def switch_do(driver,func):
	"切换到最新打开的窗口，执行函数func，之后关闭窗口，并切换到上一个窗口"
	num=len(driver.window_handles)
	driver.switch_to_window(driver.window_handles[num-1])
	func(driver)
	driver.close()
	driver.switch_to_window(driver.window_handles[num-2])

def wait_for_begin(driver):
	'等待页面更新'
	driver.set_page_load_timeout(4)
	first=True
	firInfo=""
	while True: 
		call_with_no_except(driver.refresh,None)

		try:
			# 看是否有情况是头一个不是最新的？？
			if first:
				firInfo=driver.find_element_by_class_name('s_info_name').text
				print 'firInfo=',firInfo
				first=False
			else:
				curInfo=driver.find_element_by_class_name('s_info_name').text
				print 'curInfo=',curInfo
				if firInfo!=curInfo:
					print 'here we go...'
					break
		except:
			pass

def move_to_ele(driver,ele,act='down'):
	action=ActionChains(driver)
	# 先向下翻页，再移动到元素
	if act=='down':
		if False: #废弃不用。虽然向下翻页更直观，但是重复10次调用，速度太慢
			i=0
			while i<10:
				i+=1
				action.key_up(selenium.webdriver.common.keys.Keys.DOWN)
			action.move_to_element(ele).perform()
		action.key_up(selenium.webdriver.common.keys.Keys.PAGE_DOWN).move_to_element(ele).perform()
	else:
		action.move_to_element(ele).perform()

#全局变量
pIdx=0
def send_to_subp(href):
	"发送购买链接给子进程"
	global pIdx
	while True:
		if ps[pIdx].poll():#某些子进程已经出错退出了
			del ps[pIdx]
			print pIdx,'process quits by accident'
			if ps:
				pIdx=(pIdx+1)%len(ps)
			else:
				print 'all processes are dead...'
				sys.exit(0) #退出
		else:
			break
	ps[pIdx].stdin.write(href)
	pIdx=(pIdx+1)%len(ps)

def own_pick(driver,sizeIdx,dts):
	idx=0
	pIdx=0
	ele=dts[idx]
	move_to_ele(driver,ele)
	print local_str('可以开始控制了：通过1，2，3，4选取物品,通过j和k控制窗口移动')
	while True:
		c=''
		if IsWindows:
			c=msvcrt.getch()
			print local_str('您输入了'),c
		else:
			#rlist,_,_=select([sys.stdin],[],[])
			c=sys.stdin.read(1)
			print local_str('\n您输入了'),c
		if c=='j': #向下
			idx+=4
			#if IsWindows and idx%16==0: #windows下每4行要重新获取一下dts，因为是异步加载
				#dts=driver.find_elements_by_class_name('pro_list_pic')
			try: ele=dts[idx] #选取的内容越界了，函数返回
			except: 
				print local_str('进入下一页')
				return
			move_to_ele(driver,ele)
		elif c=='k': #向上
			if idx>=4:
				idx-=4
				ele=dts[idx] 
				move_to_ele(driver,ele,'')
		elif c=='1' or c=='2' or c=='3' or c=='4':
			no=idx+int(c)-1
			try: ele=dts[no] #选取的内容越界了，继续循环
			except : continue
			href=ele.find_element_by_tag_name("a").get_attribute('href')+' '+sizeIdx+Line
			send_to_subp(href)
		elif c=='q':
			raise Exception #退出

def auto_pick(driver,sizeIdx,dts):
	for dl in driver.find_elements_by_class_name('J_pro_items'):
		try:
			title=dl.find_element_by_class_name('pro_list_tit').text
			print 'test',title
			if not filter(lambda x:x in title,Excepts) and filter(lambda x:x in title,Keywords)==Keywords:
				price=dl.find_element_by_tag_name("em").text.lstrip(u'¥')
				discount=dl.find_element_by_xpath("./dd[@class='pro_list_data']/span").text
				discount=re.search(r'\((.*)\)',discount).group(1).rstrip(u'折')
				print 'price=',price,'discount=',discount
				if float(PriceSpan[0])<=float(price)<=float(PriceSpan[1]) and float(DisSpan[0])<=float(discount)<=float(DisSpan[1]):
					print 'pick it'
					href=dl.find_element_by_tag_name('a').get_attribute('href')+' '+sizeIdx+Line
					send_to_subp(href)
		except Exception as e: #忽略可能出现的StaleElementReferenceException错误
			print e
	

def control(driver,sizeIdx):
	"在一页上处理用户按键"
	# xpath有bug，不能[@aa='aa'][2]
	dts=driver.find_elements_by_class_name('pro_list_pic')

	if not IsWindows: # 滚动到最底端in linux
		action=ActionChains(driver)
		action.key_up(selenium.webdriver.common.keys.Keys.END) # 还有send_keys 或 key_down
		i=0
		while i<3: #至少3次才可以保证100个商品完全出现
			i=i+1
			action.perform()
	else: # in windows 待测试？？？？
		i=0
		while i<3: 
			i+=1
			action=ActionChains(driver)
			action.move_to_element(dts[-1]).perform()
			dts=driver.find_elements_by_class_name('pro_list_pic')

	if AutoPickMode:
		auto_pick(driver,sizeIdx,dts)
	else:
		own_pick(driver,sizeIdx,dts)

def process(driver):
	"处理每一个品牌"
	# 页面内又含有分支页面
	global Depth
	if Depth<=1: #深度最多为1层
		try: url=driver.current_url
		except TimeoutException: pass
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
					print 'go into '+ele.get_attribute('href')
					switch_do(driver,process)
			Depth-=1
			return

	sizeIdx=-1
	for type,size in zip(Type,Size):
		print type,size
		has_more=True
		num=1
		sizeIdx+=1
		while has_more:
			# 加载新页
			try:
				url=driver.current_url
			except TimeoutException:
				pass
			idx=driver.current_url.find('?')
			originUrl=''
			if idx!=-1:
				originUrl=driver.current_url[0:idx]
			else:
				originUrl=driver.current_url
			# lower()!!!
			new_url=originUrl+"?q=0|%s|%s|%s|%s|%d"%(TYPE[type],SIZE[size.lower()],EMPTY[Empty],SORT[Sort],num)
			print new_url
			driver.set_page_load_timeout(3) #3s超时
			call_with_no_except(driver.get,new_url)

			num+=1
			# 判断是否存在
			try: 
				driver.find_element_by_class_name('pro_find_none')
			except NoSuchElementException:
				pass
			else: 
				print local_str('不存在该类别的商品')
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
	'搜需要的品牌'
	try: #如果找不到，就直接return
		lis=driver.find_elements_by_class_name(item)
	except:
		print local_str('没有'+item+'条目，返回')
		return
	#driver.set_page_load_timeout(0.5) #0.5s超时,太短的话(0.1s)click可能会超时
	driver.set_page_load_timeout(4) #等待嵌套页面加载需要的时间较长
	for li in lis:
		info=li.find_element_by_class_name(name).text
		print info
		# 至少包括Brands里的一项，包括Keys里的所有项
		if filter(lambda x: x in info,Brands) and ( Keys and Keys==filter(lambda x:x in info,Keys) or not Keys ):
			if u"男女" in info:
				MixFlag=True
			print 'before click'
			action=ActionChains(driver)
			action.click(li).perform()
			print 'after click'
			# 切换到新的窗口
			print 'go into '+info
			switch_do(driver,process)
			MixFlag=False

def call_with_no_except(func,arg=None):
	try:
		if arg:
			func(arg)
		else:
			func()
	except:
		pass


if __name__=='__main__':
	try:
		# 命令行不缓冲直接读入，linux版本
		if not IsWindows and not AutoPickMode:
			fd = sys.stdin.fileno()
			old = termios.tcgetattr(fd)
			new = termios.tcgetattr(fd)
			new[3] = new[3] & ~termios.ICANON
			termios.tcsetattr(fd, termios.TCSADRAIN, new)

		forks()
		print 'after forks'
	
		driver=webdriver.Chrome()
		driver.set_window_position(0,0)
		driver.set_window_size(ScreenW,ScreenH1)

		if IsWindows:
			driver.set_page_load_timeout(30)#win下chrome第一个页面加载很慢
		else:
			driver.set_page_load_timeout(8)
		call_with_no_except(driver.get,HomeUrl)

		if TestMode:
			# 如果不执行wait_for_begin，就必须刷新一次，否则选地址的div挡着没法点击链接
			print 'TestMode'
			#ele=WebDriverWait(driver,60,2,(Exception)).until(lambda x:x.find_element_by_class_name('sdf_item'))
			driver.set_page_load_timeout(40)#40s超时,等待第一次加载
			call_with_no_except(driver.refresh)
		else:
			print 'Non-TestMode'
			wait_for_begin(driver)

		print 'after wait_for_begin'

		# 展示区
		search_brand('sdf_item','sdf_name') #class='sdf_item sdf_item_only'也包括在内
		# 今日新品
		search_brand('s_mod','s_info_name')
		
	except Exception as e:
		print e
	finally:
		driver.quit()

		for p in ps:#通知子进程退出，或最大化
			print 'inform process to quit'
			p.stdin.write('q'+Line)

		# linux下取消命令行no-buffer模式
		if not IsWindows and not AutoPickMode:
			termios.tcsetattr(fd, termios.TCSADRAIN, old)

