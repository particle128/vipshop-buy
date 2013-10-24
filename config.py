#!/usr/bin/env python
# coding=utf-8

from ConfigParser import RawConfigParser
import codecs

CONFIG_FILE='config.ini'
W_CONFIG_FILE='config_w.ini'

# 常量区
LoginUrl=''
HomeUrl=''
TYPE={}
SIZE={}
EMPTY={}
SORT={}
#电脑屏幕大小
ScreenW=0
ScreenH1=0
ScreenH2=0
# 可配置区
Account=[]
Keys=[]
# 常用配置区
TestMode=False
Debug=False
Brands=[]
Type=[]
Size=[]
Empty=''
Sort=''
#自动模式
AutoPickMode=False 
PriceSpan=[]
DisSpan=[]
Excepts=[]
Keywords=[]
#超时
BuyTimeout=0

def pOpt():
	for name,val in globals().items():
		#不含有下划线的
		if not name.count('__'):
			print name,val

'获取全部的配置文件中的选项'
cf=RawConfigParser()
cf.readfp(codecs.open(CONFIG_FILE,'r','utf-8'))
#url
LoginUrl=cf.get('url','LoginUrl')
HomeUrl=cf.get('url','HomeUrl')
#type
for option,value in cf.items('type'):
	TYPE[unicode(option)]=value
for t in cf.get('type','Type').split(' '):
	Type.append(unicode(t))
#size
for option,value in cf.items('size'):
	SIZE[unicode(option)]=value
for s in cf.get('size','Size').split(' '):
	Size.append(unicode(s))
#empty
for option,value in cf.items('empty'):
	EMPTY[unicode(option)]=value
Empty=unicode(cf.get('empty','Empty'))
#sort
for option,value in cf.items('sort'):
	SORT[unicode(option)]=value
Sort=unicode(cf.get('sort','Sort'))
#screen
ScreenW=cf.getint('screen','ScreenW')
ScreenH1=cf.getint('screen','ScreenH1')
ScreenH2=cf.getint('screen','ScreenH2')
#auto_pick
AutoPickMode=cf.getboolean('auto_pick','AutoPickMode')
if AutoPickMode:
	PriceSpan=cf.get('auto_pick','PriceSpan').split(',')
	DisSpan=cf.get('auto_pick','DisSpan').split(',')
	Excepts=cf.get('auto_pick','Excepts').split(',')
	Keywords=cf.get('auto_pick','Keywords').split(',')
#config
Debug=cf.getboolean('config','Debug')
TestMode=cf.getboolean('config','TestMode')
for acc in cf.get('config','Account').split('\n'):
	Account.append((acc.split(':')[0],acc.split(':')[1]))
for key in cf.get('config','Keys').split(' '): 
	Keys.append(unicode(key)) 
for brand in cf.get('config','Brands').split(' '):
	Brands.append(unicode(brand))
#timeout
cf1=RawConfigParser()
cf1.read(W_CONFIG_FILE)
BuyTimeout=cf1.getfloat('timeout','buytimeout')
print '原BuyTimeout为:',BuyTimeout

if Debug:
	print LoginUrl
	pOpt()

def timeout_inc(inc):
	'修改配置文件的超时时间BuyTimeout'
	cur=BuyTimeout+inc
	global cf1
	cf1.set('timeout','buytimeout',str(cur))
	with open(W_CONFIG_FILE,'wb') as configFile:
		cf1.write(configFile)
	print '新BuyTimeout已设置为:'+str(cur)

