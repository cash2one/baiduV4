# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:49:58 2017

@author: WddIs
"""

from datetime import datetime


class checker(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def check_time(self):
        nowtime = datetime.now()
        if self.start <= nowtime.hour < self.end:
            return 0
        else:
            newtime = datetime.now().replace(hour=self.start, minute=0, second=0)
            diff = (newtime - nowtime).total_seconds()
            if diff < 0:
                return 24 * 3600 + diff
            else:
                return diff
