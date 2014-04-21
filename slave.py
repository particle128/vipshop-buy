#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function  # 必须要出现在文件开头
import time
import sys
import re
import os
import signal

from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from config import *

# MaxReload = 2  # reload的最大次数
HasGood = False
# TimeoutCnt = 0  # 超时计数
SuccessCnt = 0  # 连续成功计数
State = 'ExponState' # 最初是指数增长阶段


def p_print(*args):
    '''带有pid的输出'''
    print(os.getpid(), ':', end='')
    for arg in args:
        print(arg, end=' ')
    print('\n', end='')


def buy(driver, size):
    "购买对应尺码的商品"
    p_print('buy')
    SizeReg = ''
    if size != u'默认':
        SizeReg = u'^' + size + u'([^.L]|$)'
    else:  # 如果是默认尺码，那就所有商品都选
        SizeReg = u'.*'
    timeout_flag = False
    ref = False
    global BuyTimeout, SuccessCnt, State
    while True:
        try:
            if ref:
                driver.refresh()
            # 定位出价格显示区
            pri_block=driver.find_element_by_class_name("size_list")
            btn = driver.find_element_by_id('J_cartAdd_submit')
            for li in pri_block.find_elements_by_tag_name('li'):
                # 没有售完，且大小符合要求
                class_attr = li.get_attribute('class')
                if class_attr and 'sli_disabled' in class_attr:  # 售完的
                    continue
                span = li.find_element_by_tag_name('span')
                print("test",span.text)
                if re.search(SizeReg, span.text.strip('" ')):
                    action = ActionChains(driver)
                    # ！！！ click会超时，至少2s的page_load_timeout
                    action.click(li).click(btn).perform()
                    p_print('got size', span.text.strip())
                    global HasGood  # !!!全局变量
                    HasGood = True
                    time.sleep(1)
        except TimeoutException:
            p_print('timeout')
            ref=False
        except Exception as e:
            p_print(e)
            timeout_flag = True

            if State == 'ExponState':
                BuyTimeout*=2    # 指数增长
            else:
                BuyTimeout+=1    # 线性调整
                if State == 'LinearState':
                    State = 'FinalState'

            driver.set_page_load_timeout(BuyTimeout) 
            p_print('new timeout')
            ref=True#重新加载该页
        else:
            break

    if not timeout_flag:
        if State == 'ExponState':
            SuccessCnt += 1
            if SuccessCnt == 2:
                State = 'LinearState' # 指数增长阶段，连续两次不超时，进入线性调整阶段
        elif State == 'LinearState':
            BuyTimeout-=1      # 线性调整
        else:
            pass # FinalState不进行-1的操作
    elif State == 'ExponState':
        SuccessCnt = 0



def login(driver, user, pwd):
    driver.get(LoginUrl)
    driver.find_element_by_id("J_L_name").send_keys(user)
    driver.find_element_by_id('J_L_psw').send_keys(pwd)
    driver.find_element_by_id("user_login_form").submit()
    driver.back()  # !!!


if __name__ == '__main__':

    p_print('slave')
    user, pwd, xpos = sys.argv[1], sys.argv[2], sys.argv[3]
    p_print(user, pwd)
    while True:  # 防止调用Chrome出错
        try:
            driver = webdriver.Chrome()
        except:
            time.sleep(2)
        else:
            break

    driver.set_window_size(ScreenW / len(Account), ScreenH2)
    driver.set_window_position(int(xpos), ScreenH1)
    login(driver, user, pwd)

    try:
        driver.set_page_load_timeout(BuyTimeout)  # 从配置文件读取timeout值
        while True:
            infos = sys.stdin.readline()  # !!!read()不行，是全缓冲的
            # 退出
            if infos.find('q') == 0:  # 开头是q的，表示退出
                set_timeout() # 修改配置文件里的timeout
                if HasGood:
                    p_print('has goods')
                    driver.maximize_window()  # 最大化有物品的窗口
                    # 停止
                    while True:
                        signal.pause()
                else:
                    p_print('has no goods')
                    break
            href = infos.split()[0]
            sizeIdx = int(infos.split()[1])
            size = Size[sizeIdx]
            p_print(href, size)
#            cpid = os.fork()
#            if cpid == 0:
#                p_print('child: before get')
#                driver.get(href)
#                p_print('child: after get')
#                os._exit(0)
#
#            try:
#                p_print('parent: before until')
#                pri_block = WebDriverWait(driver, 5).until(
#                    EC.presence_of_element_located((By.CLASS_NAME, 'size_list')))
#                btn = WebDriverWait(driver, 5).until(
#                    EC.element_to_be_clickable((By.CLASS_NAME, 'J_cartAdd_submit')))
#                p_print('parent: after until')
#                # kill the child process
#                os.kill(cpid, signal.SIGKILL)
#                p_print('parent: after kill')
#                status = os.waitpid(cpid, os.WNOHANG)[1]
#                if os.WIFSIGNALED(status):
#                    p_print('term signal:', os.WTERMSIG(status))
#                elif os.WIFEXITED(status):
#                    p_print('exit code:', os.WEXITSTATUS(status))
#                else:
#                    p_print('unknown waitstatus')
#            except Exception as e:
#                p_print('parent error:',e)
#            else:
#                buy(driver, size, pri_block)
            try:
                driver.get(href)
            except TimeoutException:
                pass
            buy(driver, size)
    except Exception as e:
        p_print('error:', e)
    finally:
        driver.quit()
