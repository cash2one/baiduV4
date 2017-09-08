# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:49:58 2017

@author: WddIs
"""
import json
import os

from checkWorkTime import checker
from clickLaunch import main
from clickWorker import clearDrivers
import multiprocessing
import logging
import time


def load(configfile):
    with open(configfile) as json_file:
        data = json.load(json_file)
        return data


config = load("config.json")
timechecker = checker(config["starttime"], config["endtime"])


def initLogging(name='monitor'):
    """Init for logging
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s %(asctime)s [line:%(lineno)d]%(filename)s %(message)s',
        datefmt='%d-%b-%Y %H:%M:%S',
        filename=name + '.log',
        filemode='a')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(levelname)s %(asctime)s [line:%(lineno)d]%(filename)s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


if __name__ == "__main__":
    DIR = "launchlogs"
    FILE = "baidusearch.log"
    initLogging()
    logging.info("monitor start")
    p = multiprocessing.Process(target=main)
    p.daemon = True
    timestamp = 10*60

    fn = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
    try:
        with open(DIR + '/' + FILE, "r") as lf:
            ln = len(lf.readlines())
    except:
        ln = 0

    while 1:
        if not p:
            p = multiprocessing.Process(target=main)
            p.daemon = True
            p.start()
        if not p.is_alive():
            p.start()
        logging.info("baiduSearch launch")
        time.sleep(timestamp)

        with open(DIR + '/' + FILE, "r") as lf:
            nln = len(lf.readlines())
            nfn = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
            if nfn > fn:
                logging.info("新的日志文件，%d-%d --> %d-%d" % (fn, ln, nfn, nln))
                fn = nfn
                ln = nln
            if nln - ln > 2:
                logging.info("日志有更新，%d-%d --> %d-%d" % (fn, ln, fn, nln))
                ln = nln
            else:
                diff = timechecker.check_time()
                if diff != 0:
                    logging.warning("程序休息 %ds/%dm/%dh" % (diff, diff / 60, diff / 60 / 60))
                    time.sleep(diff)
                    continue
                else:
                    logging.warning("%d s 日志没有更新，重启Launch进程。" % timestamp)
                    p.terminate()
                    p = None
                    clearDrivers()
                    time.sleep(10)
