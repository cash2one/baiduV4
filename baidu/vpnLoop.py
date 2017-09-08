# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:49:58 2017

@author: WddIs
"""

import subprocess as subp
import os
import logging

import time

if os.name == 'nt':
    startupinfo = subp.STARTUPINFO()
    startupinfo.dwFlags |= subp.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subp.SW_HIDE
else:
    startupinfo = None


class vpnRandom(object):
    count = 0

    def __init__(self, ovpns=None):
        if ovpns:
            self.ovpnfiles = ovpns
        else:
            self.ovpnfiles = [
                [u"全国1", u"全国1.ovpn"],
                [u"全国2", u"全国2.ovpn"],
                [u"云南省", u"云南省.ovpn"],
                [u"北京", u"北京.ovpn"],
                [u"吉林省", u"吉林省.ovpn"],
                [u"四川省", u"四川省.ovpn"],
                [u"安徽省", u"安徽省.ovpn"],
                [u"山东省", u"山东省.ovpn"],
                [u"山西省", u"山西省.ovpn"],
                [u"江苏省", u"江苏省.ovpn"],
                [u"江西省", u"江西省.ovpn"],
                [u"河南省", u"河南省.ovpn"],
                [u"浙江省", u"浙江省.ovpn"],
                [u"湖北省", u"湖北省.ovpn"],
                [u"湖南省", u"湖南省.ovpn"],
                [u"福建省", u"福建省.ovpn"],
                [u"辽宁省", u"辽宁省.ovpn"],
            ]
        self.filenum = len(self.ovpnfiles) - 1

    def connectVPN(self):
        ovpn = self.ovpnfiles[self.count % self.filenum]
        cmd = "openvpn ./ovpnfile/" + ovpn[1].encode("gb2312")
        btime = time.time()
        for i in range(3):
            process = subp.Popen(cmd, stdout=subp.PIPE, bufsize=1, startupinfo=startupinfo)
            for line in iter(process.stdout.readline, b''):
                if time.time() - btime > 60:
                    logging.error("%s vpn : more than 60s! give up!", ovpn[0])
                    self.count += 1
                    return None
                if "Initialization Sequence Completed" in line:
                    logging.info("%s vpn : connected!", ovpn[0])
                    time.sleep(3)
                    return process
        logging.error("%s vpn : connect fail!", ovpn[0])
        self.count += 1
        return None

    def disconnect(self, process):
        ovpn = self.ovpnfiles[self.count % self.filenum]
        process.terminate()
        logging.info("%s vpn : disconnected!", ovpn[0])
        process.kill()
        self.count += 1
        time.sleep(3)

