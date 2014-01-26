# coding=utf-8


def switch_do(driver, func, url=None):
    '''切换到最新打开的窗口，执行函数func，之后关闭窗口，并切换到上一个窗口'''
    num = len(driver.window_handles)
    driver.switch_to_window(driver.window_handles[num-1])
    try:
        url=driver.current_url
    except:
        pass
    if url:
        func(driver,url)
    else:
        func(driver,driver.current_url)
    driver.close()
    driver.switch_to_window(driver.window_handles[num-2])


def call_ignore(func,arg=None):
    '''忽略异常的调用'''
    try:
        if arg:
            func(arg)
        else:
            func()
    except:
        pass


def wait_for_begin(driver):
    '''等待页面更新'''
    driver.set_page_load_timeout(4)
    first=True
    firInfo=""
    while True: 
        call_ignore(driver.refresh,None)
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

