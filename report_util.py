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
import datetime

from jinja2 import Environment, PackageLoader


class Report:

    def __init__(self, report_dir):
        self.report_dir = report_dir
        self.env = Environment(loader=PackageLoader('report_util', 'templates'))

        self.basic_template = self.env.get_template('report_template.html')
        self.data_charts_template = self.env.get_template('data_charts_template.html')

        self.basic_report_name = os.path.join(self.report_dir, 'basic_report.html')
        self.data_charts_name = os.path.join(self.report_dir, 'data_charts.html')

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
            detail['xpath'] = '//' + item[4].split('//')[-1]
            detail['log'] = item[5]
            if item[5] == 'pass':
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
        # get basic test data
        params = self.load_data()

        # get activity count data
        activity_count = self.activity_count(params)
        # copy css and js from templates to report dir.
        css_dir = os.path.join(self.report_dir, 'css')
        js_dir = os.path.join(self.report_dir, 'js')
        img_dir = os.path.join(self.report_dir, 'img')
        os.mkdir(css_dir)
        os.mkdir(js_dir)
        os.mkdir(img_dir)

        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        src_css_dir = os.path.join(template_dir, 'css')
        src_js_dir = os.path.join(template_dir, 'js')
        src_img_dir = os.path.join(template_dir, 'img')

        for src_css_file in os.listdir(src_css_dir):
            shutil.copy(os.path.join(src_css_dir, src_css_file), css_dir)
        for src_js_file in os.listdir(src_js_dir):
            shutil.copy(os.path.join(src_js_dir, src_js_file), js_dir)
        for src_img_file in os.listdir(src_img_dir):
            shutil.copy(os.path.join(src_img_dir, src_img_file), img_dir)

        # copy index html
        index_html_path = os.path.join(template_dir, 'index.html')
        shutil.copy(index_html_path, self.report_dir)

        # render basic report
        with open(self.basic_report_name, 'w', encoding='utf-8') as f:
            content = self.basic_template.render(activities=params)
            f.write(content)

        # render activity count report
        with open(self.data_charts_name, 'w', encoding='utf-8') as f:
            content = self.data_charts_template.render(activity_chart=activity_count)
            f.write(content)

    @staticmethod
    def activity_count(param):
        data = {'pie': [], 'histogram': {'xAxis': [], 'count': []}, 'event_total': 0}
        activity_short_re = re.compile(r'\.([a-zA-Z0-9]+)Activity$')
        event_total = 0
        for name, value in param.items():
            short_name = activity_short_re.search(name)
            if short_name is None:
                short_name = name
            else:
               short_name = short_name.groups()[0]
            activity = {}
            total = value['pass'] + value['error']
            event_total += total
            activity['name'] = short_name
            activity['value'] = total
            data['pie'].append(activity)
            data['histogram']['xAxis'].append(short_name)
            data['histogram']['count'].append(total)
        data['event_total'] = event_total
        data_json = json.dumps(data)
        return data_json

    def clear_expired_report(self, expired_day):
        root_reports = os.path.join(self.report_dir, '..')
        days = datetime.timedelta(days=expired_day)
        expired_date = datetime.datetime.now() - days
        expired_date = int(expired_date.strftime('%Y%m%d%H%M%S'))
        for report in os.listdir(root_reports):
            report_date = int(report.split('_')[0])
            if report_date < expired_date:
                self.rec_remove_file(os.path.join(root_reports, report))
            else:
                break

    @staticmethod
    def rec_remove_file(dir):
        res = os.walk(dir)
        for _dir, _, files in reversed(list(res)):
            for file in files:
                os.remove(os.path.join(_dir, file))
            os.rmdir(_dir)


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
                    crash_time = str(datetime.datetime.now().year) + ' ' + data
                    time_array = datetime.datetime.strptime(crash_time, '%Y %m-%d %H:%M:%S.%f')
                    timestamp = int(time_array.timestamp())
                    log_detail += line
                else:
                    log_detail += line
            else:
                if log_detail and timestamp:
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


if __name__ == '__main__':
    path = os.path.join(os.path.dirname(__file__), 'reports', '20210401195612_FA7B91A04880')
    r = Report(report_dir=path)
    r.clear_expired_report(expired_day=5)



