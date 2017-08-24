# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:49:58 2017

@author: WddIs
"""
import json
import logging as log
import random
import subprocess as subp
import time
import threading

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
        pass

    def articleTask(self, ua, url):
        dcap = DesiredCapabilities.PHANTOMJS.copy()
        dcap["phantomjs.page.settings.loadImages"] = False
        dcap["phantomjs.page.settings.resourceTimeout"] = 15
        dcap["phantomjs.page.settings.userAgent"] = ua
        try:
            driver = webdriver.PhantomJS(desired_capabilities=dcap)
        except Exception, e:
            log.exception(e)
            return
        try:
            driver.get(url)
        except Exception, e:
            log.exception(e)
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
            log.exception(e)
        log.info("=================\n%s\t%s" % (url, count))
        print("=================\n%s\t%s" % (url, count))
        driver.quit()


if __name__ == "__main__":
    config = load("config.json")
    uas = config["uas"]
    urls = config["urls"] + config["urls_no"]
    log.info("A----R----T----I----C----L----E----S")

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

        log.info("5 over")
