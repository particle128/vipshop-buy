# coding=utf-8

from selenium.webdriver.common import keys
from selenium.webdriver.common.action_chains import ActionChains
import platfm
import proc

def move_to_ele(driver,ele,act='down'):
    action=ActionChains(driver)
    # 先向下翻页，再移动到元素
    if act=='down':
        if False: #废弃不用。虽然向下翻页更直观，但是重复10次调用，速度太慢
            i=0
            while i<10:
                i+=1
                action.key_up(keys.Keys.DOWN)
            action.move_to_element(ele).perform()
        action.key_up(keys.Keys.PAGE_DOWN).move_to_element(ele).perform()
    else:
        action.move_to_element(ele).perform()

def own_pick(driver,sizeIdx,dts):
    print 'own_pick begins...'
    idx=0
    pIdx=0
    ele=dts[idx]
    move_to_ele(driver,ele)
    print platfm.local_str('可以开始控制了：通过1，2，3，4选取物品,通过j和k控制窗口移动')
    while True:
        c=platfm.read_terminal()
        if c=='j': #向下
            idx+=4
            try: ele=dts[idx] #选取的内容越界了，函数返回
            except: 
                print platfm.local_str('进入下一页')
                return
            move_to_ele(driver,ele)
        elif c=='k': #向上
            if idx>=4:
                idx-=4
                ele=dts[idx] 
                move_to_ele(driver,ele,'')
        elif c=='1' or c=='2' or c=='3' or c=='4':
            no=idx+int(c)-1
            try: 
                ele=dts[no] #选取的内容越界了，继续循环
            except : 
                continue
            href=ele.find_element_by_tag_name("a").get_attribute('href')+' '+sizeIdx+platfm.Line
            proc.send_to_subp(href)
        elif c=='q':
            raise Exception #退出
    print 'own_pick ends...'

