# coding=utf-8

import subprocess
from config_local import *
from platfm import *

ps=[] #子进程列表

def forks():
	'''创建多个进程'''
	xpos=0
	for user,pwd in Account:
		cmd = slave_cmd()
		cmd += [user,pwd,str(xpos)]
		ps.append(subprocess.Popen(cmd,stdin=subprocess.PIPE))
		print user,pwd,xpos,'slave.py'
		xpos += ScreenW/len(Account)


#全局变量
pIdx=0
def send_to_subp(href):
	'''发送购买链接给子进程'''
	global pIdx
	while True:
		if ps[pIdx].poll():#某些子进程已经出错退出了
			# !!!wait进程，防止产生僵死进程
			ps[pIdx].communicate()
			del ps[pIdx]
			print pIdx,'process quits by accident'
			if ps:
				pIdx=(pIdx+1)%len(ps)
			else:
				print 'all processes are dead...'
				sys.exit(1) #退出
		else:
			break
	ps[pIdx].stdin.write(href)
	pIdx=(pIdx+1)%len(ps)


def inform_subp():
	'''通知子进程退出，或最大化'''
	for p in ps:
		print 'inform process to quit'
		p.stdin.write('q'+Line)


