#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10
import json
import os
import re
import subprocess
import shutil
from collections import namedtuple, defaultdict
from datetime import datetime

from jinja2 import Environment, PackageLoader


class Report:

    def __init__(self, report_dir):
        self.report_dir = report_dir
        self.env = Environment(loader=PackageLoader('report_util', 'templates'))
        self.template = self.env.get_template('report_template.html')
        self.report_name = os.path.join(self.report_dir, 'app_crawler_report.html')

    def load_data(self):
        with open(os.path.join(self.report_dir, 'log.json'), 'r', encoding='utf8') as fp:
            data = json.load(fp)

        data_detail = {'pass': 0, 'error': 0, 'pass_detail': None, 'error_detail': None}
        data_dict = defaultdict(lambda: dict(data_detail))
        for item in data:
            # get activity name {item[3]}
            content = data_dict[item[3]]
            # create detail dict.
            detail = dict()
            detail['before_click'] = os.path.join('screenshot', item[1])
            detail['after_click'] = os.path.join('screenshot', item[2])
            detail['xpath'] = item[4]
            detail['log'] = item[-1]
            if item[-1] == 'pass':
                content['pass'] += 1
                # check pass_detail value is None.
                if content['pass_detail']:
                    content['pass_detail'].append(detail)
                else:
                    content['pass_detail'] = [detail]
            else:
                content['error'] += 1
                if content['error_detail']:
                    content['error_detail'].append(detail)
                else:
                    content['error_detail'] = [detail]
        return data_dict

    def generate_report(self):
        params = self.load_data()
        # copy css and js from templates to report dir.
        css_dir = os.path.join(self.report_dir, 'css')
        js_dir = os.path.join(self.report_dir, 'js')
        os.mkdir(css_dir)
        os.mkdir(js_dir)
        src_css_dir = os.path.join(os.path.dirname(__file__), 'templates', 'css')
        src_js_dir = os.path.join(os.path.dirname(__file__), 'templates', 'js')
        for src_css_file in os.listdir(src_css_dir):
            shutil.copy(os.path.join(src_css_dir, src_css_file), css_dir)
        for src_js_file in os.listdir(src_js_dir):
            shutil.copy(os.path.join(src_js_dir, src_js_file), js_dir)
        report_content = self.template.render(activities=params)
        with open(self.report_name, 'w', encoding='utf-8') as f:
            f.write(report_content)


class LogAndroid:

    def __init__(self, udid):
        self.__udid = udid
        self.__log_clear = 'adb -s {} logcat -c'.format(self.__udid)
        self.__crash_log = 'adb -s {} logcat -b crash'.format(self.__udid)

    def clear_log(self):
        while True:
            p = subprocess.Popen(self.__log_clear, shell=True, encoding='utf8',
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if not p.stdout.read():
                break

    def collect_log(self, report_path):
        log_path = os.path.join(report_path, 'log.txt')
        with open(log_path, 'w', encoding='utf8') as f:
            p = subprocess.Popen(self.__crash_log, shell=True, encoding='utf8',
                                 stdout=f, stderr=subprocess.PIPE)
            try:
                p.wait(timeout=4)
            except subprocess.TimeoutExpired:
                pass
            finally:
                p.terminate()


class GenerateJson:

    crash = namedtuple('crash', ['time', 'log'])

    def __init__(self, report_path, record):
        self.report_path = report_path
        self.record = record
        self.__crash_log = []

    @property
    def crash_log(self):
        return self.__crash_log

    def extract_crash_log(self):
        search_crash = re.compile(r'.*FATAL EXCEPTION.*')
        log_path = os.path.join(self.report_path, 'log.txt')
        with open(log_path, 'r') as f:
            log_detail = ''
            timestamp = None
            for line in f.readlines():
                if search_crash.search(line):
                    if log_detail:
                        if timestamp:
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
                if log_detail:
                    self.__crash_log.append(self.crash(timestamp, log_detail))

    def insert_crash_log(self):
        self.extract_crash_log()
        if self.__crash_log:
            for log in self.__crash_log:
                timestamp = int(log.time)
                position = self.__search(timestamp)
                event = self.record[position]
                event = event._replace(status=str(timestamp) + '\n' + log.log)
                self.record[position] = event

    def generate_json(self):
        json_path = os.path.join(self.report_path, 'log.json')
        with open(json_path, 'w', encoding='utf-8') as fp:
            json.dump(self.record, fp)

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
                ans = mid
                left = mid + 1
        else:
            return ans












