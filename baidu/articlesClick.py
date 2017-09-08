# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:49:58 2017

@author: WddIs
"""
import json
import random
import subprocess as subp
import time
import threading

import logging
from logging.handlers import RotatingFileHandler

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def clearDrivers():
    cmd1 = "taskkill /im chromeself.driver.exe /f"
    subp.Popen(cmd1, shell=True)
    cmd2 = "taskkill /im phantomjs.exe /f"
    subp.Popen(cmd2, shell=True)
    time.sleep(2)


def load(configfile):
    with open(configfile) as json_file:
        data = json.load(json_file)
        return data


class ArticleWorker:
    def __init__(self):
        self.log = initLogging()

    def articleTask(self, ua, url):
        dcap = DesiredCapabilities.PHANTOMJS.copy()
        dcap["phantomjs.page.settings.loadImages"] = False
        dcap["phantomjs.page.settings.resourceTimeout"] = 15
        dcap["phantomjs.page.settings.userAgent"] = ua
        try:
            driver = webdriver.PhantomJS(desired_capabilities=dcap)
        except Exception, e:
            self.log.exception(e)
            return
        try:
            driver.get(url)
        except Exception, e:
            self.log.exception(e)
            return
        count = "?"
        try:
            if "blog.163.com" in url:
                count = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, '$_spaniReadCount'))).text
            elif "bbs.maicn.net" in url:
                ddd = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//p[@class="xg2"]/span[@class="xg1"]')))
                count = ddd[0].text
            elif "blog.sina.com.cn" in url:
                import re
                rid = "r_" + re.findall("/s/blog_(.*?)\.html", url)[0]
                count = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, rid))).text
            elif "zhizikeji.blog.sohu.com" in url:
                count = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "itemReadCount"))).text
            elif "wenku.baidu.com" in url:
                count = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//span[@id="doc-info-1"]'))).text
        except Exception, e:
            self.log.exception(e)
        self.log.info("=================\n%s\t%s" % (url, count))
        driver.quit()


def initLogging(name='articllogs/article'):
    """Init for logging
    """
    logging.basicConfig()
    filehandler = RotatingFileHandler(name+'.log', maxBytes=1024)
    filehandler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s %(asctime)s [line:%(lineno)d]%(filename)s %(message)s')
    filehandler.setFormatter(formatter)
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use

    # tell the handler to use this format
    console.setFormatter(formatter)
    mylog = logging.getLogger('articles')
    mylog.addHandler(filehandler)
    mylog.addHandler(console)
    return mylog


if __name__ == "__main__":
    config = load("config.json")
    uas = config["uas"]
    # urls = config["urls"] + config["urls_no"]

    urls = [
        "http://baijiahao.baidu.com/builder/preview/s?id=1576951990117426315",
        "http://baijiahao.baidu.com/builder/preview/s?id=1577214649671724633",
        "http://baijiahao.baidu.com/builder/preview/s?id=1577304755156786542",
        "http://bbs.maicn.net/blog-10330-513.html",
        "http://bbs.maicn.net/blog-10330-516.html",
        "http://bbs.maicn.net/blog-10330-517.html",
        "http://blog.sina.com.cn/s/blog_b85d8b9b0102x5q8.html",
        "http://blog.sina.com.cn/s/blog_b85d8b9b0102x5v7.html",
        "http://blog.sina.com.cn/s/blog_b85d8b9b0102x5x8.html",
        "http://www.jianshu.com/p/7551bec04921",
        "http://www.jianshu.com/p/9c1588a1fdbf",
        "http://www.jianshu.com/p/e843b63217f8",
        "http://zhizikeji.blog.sohu.com/324977681.html",
        "http://zhizikeji.blog.sohu.com/324991444.html",
        "http://zhizikeji.blog.sohu.com/324996028.html",
        "http://zhiziyun2016.blog.163.com/blog/static/260246014201772812836602",
        "http://zhiziyun2016.blog.163.com/blog/static/26024601420178111413333",
        "https://www.douban.com/note/634993571/",
        "https://www.douban.com/note/635423846/",
        "https://www.douban.com/note/635564032/",
        "https://zhuanlan.zhihu.com/p/28845819",
        "https://zhuanlan.zhihu.com/p/28937473",
        "https://zhuanlan.zhihu.com/p/28968291"
    ]

    while 1:
        worker = ArticleWorker()
        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=worker.articleTask, args=(random.choice(uas), random.choice(urls))))
            threads[i].setDaemon(True)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
