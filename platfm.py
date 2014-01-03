# coding=utf-8

import platform
import sys
from selenium.webdriver.common import keys
from selenium.webdriver.common.action_chains import ActionChains
from config_local import *


#global variable
IsWindows=False
Line=''

def set_nonbuf():
	''' 命令行不缓冲直接读入，linux版本'''
	fd = sys.stdin.fileno()
	old = termios.tcgetattr(fd)
	new = termios.tcgetattr(fd)
	new[3] = new[3] & ~termios.ICANON
	termios.tcsetattr(fd, termios.TCSADRAIN, new)


def init():
	'''初始化全局变量IsWindows和Line，初始化缓冲区'''
	global IsWindows
	global Line
	if platform.system()=="Windows":
		import msvcrt
		IsWindows=True
		Line='\r\n'
	else: #Linux
		import termios
		#from select import select
		Line='\n'
	
	if not IsWindows and not AutoPickMode:
		set_nonbuf()


def uninit():
	'''linux下取消命令行no-buffer模式
	其实没必要，因为进程马上就退出了，不会影响父进程：shell
	'''
	if not IsWindows and not AutoPickMode:
		termios.tcsetattr(fd, termios.TCSADRAIN, old)


def local_str(s):
	'''字符串s的输出版本'''
	if IsWindows:
		if isinstance(s,unicode):
			return s.encode('gbk')
		else:
			return s.decode('utf-8').encode('gbk')
	else:
		return s


def slave_cmd():
	'''返回子进程的调用命令'''
	if IsWindows:
		return ['slave.exe']
	else:
		return ['python', 'slave.py']


def read_terminal():
	'''从控制台读入一个字符'''
	c=''
	if IsWindows:
		c=msvcrt.getch()
		print local_str('您输入了'),c
	else:
		c=sys.stdin.read(1)
		print local_str('\n您输入了'),c
	return c


def roll_down(driver,dts):
	'''滚动到页面底端'''
	if not IsWindows: # 滚动到最底端in linux
		action=ActionChains(driver)
		action.key_up(keys.Keys.END) # 还有send_keys 或 key_down
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


def first_timeout(driver):
	'''设置第一次页面加载的超时时间'''
	if IsWindows:
		driver.set_page_load_timeout(30)#win下chrome第一个页面加载很慢
	else:
		driver.set_page_load_timeout(8)


