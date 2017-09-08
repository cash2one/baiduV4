# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:49:58 2017

@author: WddIs
"""
from logging.handlers import TimedRotatingFileHandler

from vpnLoop import vpnRandom
import time
from clickWorker import baiduWorker
from checkWorkTime import checker
import json
import subprocess as subp
import logging
import random


def initLogging(name='launchlogs/baidusearch'):
    """Init for logging
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s %(asctime)s [line:%(lineno)d]%(filename)s %(message)s',
        datefmt='%d-%b-%Y %H:%M:%S',
        filemode='w'
    )

    # 添加TimedRotatingFileHandler
    filehandler = TimedRotatingFileHandler(name + '.log', when='H', interval=1, backupCount=0)
    filehandler.setFormatter(logging.Formatter('%(levelname)s %(asctime)s [line:%(lineno)d]%(filename)s %(message)s'))
    filehandler.suffix = "%Y%m%d%H.log"

    console = logging.StreamHandler()

    logging.getLogger('').addHandler(filehandler)
    logging.getLogger('').addHandler(console)


def clearVPN():
    cmd = "taskkill /im openvpn.exe /f"
    subp.Popen(cmd, shell=True)


def load(configfile):
    with open(configfile) as json_file:
        data = json.load(json_file)
        return data


def main():
    initLogging()
    config = load("config.json")
    vpnconn = vpnRandom(config["ovpnfiles"])
    timechecker = checker(config["starttime"], config["endtime"])
    worker = baiduWorker(config["uas"])
    wds = config["wds"]
    # tarwd = config["tarwd"]
    # midwd = config["midwd"]

    logging.info("S----T----A----R----T")

    while 1:
        # 关闭vpn进程
        clearVPN()
        # 确认工作时间
        diff = timechecker.check_time()
        if diff != 0:
            logging.warning("程序休息 %ds/%dm/%dh" % (diff, diff / 60, diff / 60 / 60))
            time.sleep(diff)
            continue
            # 打开vpn
            # process = vpnconn.connectVPN()
            # if not process:
            # vpn打开失败，重新打开
            # logging.exception("vpn 打开失败,5秒后重新打开")
            # time.sleep(5)
            # continue

        # 查询ip并判断网络状态
        try:
            logging.info("ip-address: %s", worker.getIP())
        except Exception:
            logging.exception("查询ip地址失败")

        count = random.randint(5, 10)
        logging.info("work times:%d" % count)
        for i in range(count):
            wd = random.choice(wds)
            try:
                worker.baiduSpiderTask(wd=wd)
                logging.info("work complete------>")
            except Exception, e:
                logging.exception("work fail<------\n%s", e)
                i -= 1
                worker = baiduWorker(config["uas"])
                # if worktime == 3:
                #     logging.exception("执行任务出错三次，切换vpn并初始化worker")
                # worker = baiduWorker(config["uas"])
            time.sleep(3)
            # vpnconn.disconnect(process)


if __name__ == "__main__":
    main()
