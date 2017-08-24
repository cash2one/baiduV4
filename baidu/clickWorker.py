# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:49:58 2017

@author: WddIs
"""
import logging as workerlog
import random
import subprocess as subp
import time

import requests
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import json


def clearDrivers(driver_type):
    if driver_type == 1:
        cmd = "taskkill /im chromedriver.exe /f"
    else:
        cmd = "taskkill /im phantomjs.exe /f"
    subp.Popen(cmd, shell=True)
    time.sleep(5)


def load(configfile):
    with open(configfile) as json_file:
        data = json.load(json_file)
        return data


class baiduWorker(object):
    def __init__(self, uas):
        self.uas = uas
        self.ua = None
        self.driver_type = load("config.json")["driver"]

    def baiduSpiderTask(self, wd):

        dcap = DesiredCapabilities.PHANTOMJS.copy()
        # 从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
        if not self.ua:
            self.ua = self.getUA()
        dcap["phantomjs.page.settings.userAgent"] = ua = self.getUA()
        workerlog.info("set ua:[%s]" % ua)
        # 不载入图片，爬页面速度会快很多
        dcap["phantomjs.page.settings.loadImages"] = False
        # 打开带配置信息的phantomJS浏览器
        if self.driver_type == 1:
            driver = webdriver.Chrome(desired_capabilities=dcap)
        else:
            driver = webdriver.PhantomJS(desired_capabilities=dcap)
        driver.delete_all_cookies()
        self.ua = None

        driver.get("https://www.baidu.com/")
        time.sleep(2)
        try:
            elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'wd')))
        except Exception:
            workerlog.error("no wd input")
            driver.quit()
            return
        # 清空搜索框中的内容
        # elem.clear()
        elem.send_keys(unicode(wd))
        elem.send_keys(Keys.RETURN)
        try:
            WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@id="content_left"]')))
        except Exception:
            workerlog.error("no content of searching")
        try:
            elem.click()
        except Exception:
            workerlog.error(Exception)
        time.sleep(2)

        title = driver.title
        workerlog.info(title)

        # 词语联想
        bdsug = []
        relatedsearchs = []

        try:
            for p in WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'bdsug-overflow'))):
                bdsug.append(p.text)
        except Exception:
            workerlog.error("nothing about wordthinking")
        try:
            # 相关搜索
            for a in WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//div[@id="rs"]//th/a'))):
                relatedsearchs.append(a.text)
        except Exception:
            workerlog.error(Exception)

        if bdsug or relatedsearchs:
            recommand = "/".join(bdsug)
            relatedsearch = '/'.join(relatedsearchs)
            workerlog.info("%s", "\n".join([recommand, relatedsearch]))
        else:
            workerlog.exception("nothing about recommand or relatedsearch")
            # 没有相关推荐和联想词

        count = 0
        # 翻页和点击
        while count < 2:
            if count != 0:
                workerlog.info("next page------>")
                # 翻页
                try:
                    nextpage = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@id="page"]/a[@class="n"]')))[-1]
                    nextpage.click()
                    time.sleep(2)
                    WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.XPATH, '//div[@id="content_left"]')))
                except Exception:
                    workerlog.exception("go nextpage fail")
                except IndexError:
                    workerlog.warning("no more nextpage when pagecount is %d", count)
                    break

            count += 1
            # 获得主页句柄
            pagehandler = driver.current_window_handle
            # 获得前五个链接
            try:
                links = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@id="content_left"]//h3/a')))
            except Exception:
                links = []
            # 不存在链接的情况
            if links:
                links = links[:4]
                # 随机打开2~3个链接
                linknum = random.choice([1, 2])
                for i in range(linknum):
                    link = random.choice(links)
                    try:
                        # 这里会因为超时而不完全加载链接
                        link.click()
                        time.sleep(2)
                        workerlog.info("load link successful[%d/%d]" % (i + 1, linknum))
                    except Exception:
                        workerlog.warning("load link failed[%d/%d]" % (i + 1, linknum))
                    links.remove(link)
                    # 转到链接页，失败则表示没有打开链接
                    try:
                        sonhandle = driver.window_handles[1]
                        driver.switch_to.window(sonhandle)
                        driver.close()
                    except Exception:
                        workerlog.exception("没有打开链接 [%d/%d]" % (i + 1, linknum))
                    finally:
                        driver.switch_to.window(pagehandler)
            else:
                workerlog.warning("%s/%d page has no links" % (title, count))
                driver.save_screenshot("./errorsreenshots/%s%s.png" % (
                    "no links ",
                    title + str(time.time())))
                continue
        driver.quit()

    def getIP(self):
        if not self.ua:
            self.ua = self.getUA()
        request_headers = {
            'User-Agent': self.ua,
            'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en-GB; q=0.8, en; q=0.6, zh-Hans-CN; q=0.4, zh-Hans; q=0.2',
            'Connection': "keep-Alive",
            'DNT': '1',
            'Host': 'icanhazip.com',
        }

        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        # s.mount('https://', HTTPAdapter(max_retries=3))
        res = s.get(url="http://icanhazip.com/", headers=request_headers, timeout=10)
        content = res.content.strip()
        res.close()
        return content

    def getUA(self):
        self.ua = random.choice(self.uas)
        return random.choice(self.uas)
