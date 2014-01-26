#!/usr/bin/env python
# coding=utf-8

import re
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from config_local import *
import platfm
import proc
import page
import auto
import term


MixFlag = False  # 混合模式
Depth = 1  # 页面的嵌套深度


def control(driver, sizeIdx):
    '''在一页上处理用户按键'''
    dts = driver.find_elements_by_class_name('pro_list_pic')
    platfm.roll_down(driver, dts)
    print 'after roll down'
    if AutoPickMode:
        auto.auto_pick(driver, sizeIdx, dts)
    else:
        term.own_pick(driver, sizeIdx, dts)


def nest_page(driver):
    '''处理嵌套页面的情况：页面内又含有分支页面'''
    print 'in nest_page'
    global Depth
    if Depth <= 1:  # 深度最多为1层
        try:
            driver.find_element_by_class_name('pro_list_pic')
        except NoSuchElementException:
            Depth += 1
            print 'need to jump again'
            eles = driver.find_elements_by_tag_name('a')
            pattern = re.compile('show-\d+.html$')
            for ele in eles:
                if pattern.search(str(ele.get_attribute('href'))):
                    print 'before click'
                    action = ActionChains(driver)
                    action.click(ele).perform()
                    print 'after click'
                    # 切换到新的窗口
                    base_page = ele.get_attribute('href')
                    print 'go into ' + base_page
                    try:
                        driver.current_url
                    except:
                        pass
                    page.switch_do(driver, process, base_page)
            Depth -= 1
            return


def process(driver, base_page):
    '''处理每一个品牌'''
    # 暂时不处理嵌套页面
    # nest_page(driver)  # 嵌套页面
    print 'process begins...'
    sizeIdx = -1
    for type, size in zip(Type, Size):
        print type, size
        has_more = True
        num = 1
        sizeIdx += 1
        while has_more:
            # 加载新页
            new_url = base_page + \
                "?q=0|%s|%s|%s|%s|%d" % (
                    TYPE[type],
                    SIZE[size.lower()],
                    EMPTY[Empty],
                    SORT[Sort],
                    num)
            print new_url
            driver.set_page_load_timeout(3)  # 3s超时
            page.call_ignore(driver.get, new_url)
            num += 1
            print 'after get the page'
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
                attr = driver.find_element_by_class_name(
                    'page_next').get_attribute(
                    'href')
                if not attr:
                    has_more = False
            except:
                has_more = False
            print 'before control'
            control(driver, str(sizeIdx))
            print 'after control'
    print 'process ends...'


def search_brand(item, name):
    '''搜需要的品牌'''
    print 'in search_brand',item,name
    try:  # 如果找不到，就直接return
        lis = driver.find_elements_by_class_name(item)
    except:
        print platfm.local_str('没有' + item + '条目，返回')
        return
    print 'after find'
    # driver.set_page_load_timeout(0.5) #0.5s超时,太短的话(0.1s)click可能会超时
    driver.set_page_load_timeout(4)  # 等待嵌套页面加载需要的时间较长
    for li in lis:
        info = li.find_element_by_class_name(name).text
        print info
        # 至少包括Brands里的一项，包括Keys里的所有项
        if (filter(lambda x: x.lower() in info.lower(), Brands) and
                (Keys and Keys == filter(lambda x: x.lower() in info.lower(),
                 Keys) or not Keys)):
            global MixFlag
            if u"男女" in info:
                MixFlag = True
            action = ActionChains(driver)
            action.click(li).perform()
            print 'after click'
            time.sleep(5)
            print 'after sleep'
            # 切换到新的窗口
            print 'go into ' + info
            page.switch_do(driver, process)
            MixFlag = False


if __name__ == '__main__':
    try:
        platfm.init()
        proc.forks()
        print 'after forks'

        driver = webdriver.Chrome()
        driver.set_window_position(0, 0)
        driver.set_window_size(ScreenW, ScreenH1)

        # platfm.first_timeout(driver)
        page.call_ignore(driver.get, HomeUrl)
        print 'after get the homepage'

        if TestMode:
            # 如果不执行wait_for_begin，就必须刷新一次，否则选地址的div挡着没法点击链接
            print 'TestMode'
            xpath="//div[@class='area_choose']/dl[3]/dd/a[7]"
            ele=WebDriverWait(driver,30).until(EC.element_to_be_clickable((By.XPATH,xpath)))
            print 'before click'
            ele.click() # 选择地区
        else:
            print 'Non-TestMode'
            page.wait_for_begin(driver)
            print 'after wait_for_begin'

        # stop=raw_input('cont?')

        # 展示区
        # class='sdf_item sdf_item_only'也包括在内
        search_brand('sdf_item', 'sdf_name')
        # 今日新品
        search_brand('s_mod', 's_name')
    except Exception as e:
        print e
    finally:
        a=raw_input('input:')
        driver.quit()
        print 'driver quited'
        proc.inform_subp()
        print 'sended q to subps'
        platfm.uninit()
