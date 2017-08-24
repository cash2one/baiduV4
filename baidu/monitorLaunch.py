# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:49:58 2017

@author: WddIs
"""

from clickLaunch import main as cmain
from clickLaunch import initLogging
import multiprocessing
import logging
import time

if __name__=="__main__":
    ln = 0
    initLogging('monitor')
    p = multiprocessing.Process(target=cmain)
    p.daemon = True
    p.start()
    timestamp = 30*10
    with open('zzy%s.log' % (time.strftime('%Y%m%d', time.localtime(time.time()))), "rb") as w:
        ln = len(w.readlines())
    while 1:
        time.sleep(timestamp)

        with open('zzy%s.log' % (time.strftime('%Y%m%d', time.localtime(time.time()))), "rb") as w:
            nln = len(w.readlines())
            if nln-ln > 0:
                ln = nln
                logging.info("日志有更新，现在%d行。" %ln)
            else:
                logging.warning("%d s 日志没有更新，重启main进程。" %timestamp)
                p.terminate()
                p.run()
