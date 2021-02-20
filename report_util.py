#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10
import os
import re
import subprocess
import time
from collections import namedtuple
from datetime import datetime


class Report:

    def __int__(self):
        pass


class LogAndroid:

    def __init__(self, udid):
        self.log_clear = 'adb -s {} logcat -c'.format(udid)
        self.crash_log = 'adb -s {} logcat -b crash'.format(udid)
        self.report_path = os.path.join(os.path.dirname(__file__), 'report')
        if not os.path.exists(self.report_path):
            os.mkdir(self.report_path)
        self.__log_path = os.path.join(self.report_path, str(int(time.time())) + '_{}_log.txt'.format(udid))

    def clear_log(self):
        while True:
            p = subprocess.Popen(self.log_clear, shell=True, encoding='utf8',
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if not p.stdout.read():
                break

    def collect_log(self):
        with open(self.log_path, 'w', encoding='utf8') as f:
            p = subprocess.Popen(self.crash_log, shell=True, encoding='utf8',
                             stdout=f, stderr=subprocess.PIPE)
            try:
                p.wait(timeout=4)
            except subprocess.TimeoutExpired:
                pass
            finally:
                p.terminate()

    def __str__(self):
        return self.log_path

    @property
    def log_path(self):
        return self.__log_path


class GenerateJson:

    crash = namedtuple('crash', ['time', 'log'])

    def __init__(self, log_path, record):
        self.log_path = log_path
        self.record = record
        self.__crash_log = []

    @property
    def crash_log(self):
        return self.__crash_log

    def extract_crash_log(self):
        search_crash = re.compile(r'.*FATAL EXCEPTION.*')
        with open(self.log_path, 'r') as f:
            log_detail = ''
            for line in f.readlines():
                if search_crash.search(line):
                    if log_detail:
                        self.__crash_log.append(self.crash(timestamp, log_detail))
                        log_detail = ''
                    crash_time = line.split()[:2]
                    data = ' '.join(i for i in crash_time)
                    crash_time = str(datetime.now().year) + ' ' + data
                    time_array = datetime.strptime(crash_time, '%Y %m-%d %H:%M:%S.%f')
                    timestamp = int(time_array.timestamp())
                    log_detail += line
                else:
                    log_detail += line
            else:
                self.__crash_log.append(self.crash(timestamp, log_detail))

    def insert_crash_log(self):
        if self.__crash_log:
            for log in self.__crash_log:
                timestamp = int(log.time)
                position = self.__search(timestamp)
                event = self.record[position]
                event = event._replace(status=str(timestamp) + '\n' +log.log)
                self.record[position] = event

    def __search(self, timestamp: int):
        n = len(self.record)
        left = 0
        right = n - 1
        ans = 0
        while left <= right:
            mid = (left + right) // 2
            event = self.record[mid]
            if event.time == timestamp:
                return mid
            elif event.time > timestamp:
                right = mid - 1
            elif event.time < timestamp:
                ans= mid
                left = mid + 1
        else:
            return ans












