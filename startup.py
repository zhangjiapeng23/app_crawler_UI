#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10
import os
import re
import sys
import threading
from concurrent import futures

from selenium.common.exceptions import InvalidSessionIdException

from device_info_util import get_serial_numbers_android, get_serial_numbers_ios, kill_adb_server
from crawler import Crawler
from config_util import Config
from log import log
from report_util import GenerateJson, Report

class FilePathInvalid(Exception):
    '''
    file path is not valid or can't find this fiel
    '''


def print_spider():
    for i in range(6):
        print(' ' * (19 + i * 2) + '*' + ' ' * (5 - i) + '*' + ' ' * (5 - i) + '*' + ' ' * (5 - i) + '*' + ' ' * (
                    5 - i) + '*')

    print(' ' * 30 + '***')

    for i in range(7):
        print(' ' * 31 + '*')

    for i in range(6):
        if i > 2:
            print(' ' * (25 - i) + '*' + ' ' * 5 + '*' * (i * 2 + 1) + ' ' * 5 + '*')
        else:
            print(' ' * (25 - i) + '*' + ' ' * (5 + i) + '*' + ' ' * (5 + i) + '*')

    for i in range(4):
        print(' ' * (12 - i) + '*' + ' ' * (6 + i * 2) + '*' + ' ' * 5 + '*' * (13 - i * 2) + ' ' * 5 + '*' + ' ' * (
                    6 + i * 2) + '*')

    for i in range(4):
        print(' ' * (9 + i * 2) + '*' + ' ' * (12 - i * 3) + '*' * (19 + i * 2) + ' ' * (12 - i * 3) + '*')

    for i in range(4):
        print(' ' * (18 - i * 3) + '*' + ' ' * i * 4 + '*' * (25 - i * 2) + ' ' * i * 4 + '*')

    for i in range(2):
        print(' ' * 9 + '*' + ' ' * (13 - i * 2) + '*' + ' ' * i * 4 + '*' * (15 - i * 4) + ' ' * i * 4 + '*' + ' ' * (
                    13 - i * 2) + '*')

    for i in range(4):
        print(' ' * (18 + i * 2) + '*' + ' ' * (25 - i * 4) + '*')


def execute_timer(total_time, func):
    timer = threading.Timer(interval=total_time*60, function=func)
    log.info("Timer start work!!")
    timer.start()


def performer(config_path, serial, timer):
    config = Config(config_path, udid=serial)
    spider = Crawler(config, timer)
    execute_timer(spider.timer, spider.quit)
    try:
        while True:
            spider.run()
    except InvalidSessionIdException:
        # return test result.
        return spider.report_path, spider.record
        log.error('test end!')

def cmd_parse():
    necessary_param = dict()
    cmd = sys.argv[1:]
    cmd_string = ''.join(cmd)
    config_path = re.search(r'-[c|C]([^-]*)', cmd_string)
    if config_path and config_path.group(1):
        config_file = config_path.group(1)
        if os.path.exists(config_file):
            necessary_param['config'] = config_file
        elif os.path.exists(os.path.join(os.getcwd(), config_file)):
            necessary_param['config'] = os.path.join(os.getcwd(), config_file)
        elif os.path.exists(os.path.join(os.path.dirname(__file__), 'config', config_file)):
            necessary_param['config'] = os.path.join(os.path.dirname(__file__), 'config', config_file)
        else:
            error_msg = "{} is not a valid file path, please double check.".format(config_file)
            raise FilePathInvalid(error_msg)
    else:
        error_msg = "you must configure the path of config file by using '-c' param."
        raise FilePathInvalid(error_msg)

    # other param
    optional_param = dict()
    max_worker_nums = re.search(r'-[m|M]([^-]*)', cmd_string)
    run_time = re.search(r'-[t|T]([^-])*', cmd_string)
    if max_worker_nums and max_worker_nums.group(1):
        optional_param['max_workers'] = max_worker_nums.group(1)
    if run_time and run_time.group(1):
        optional_param['timer'] = run_time.group(1)

    # merger params
    necessary_param.update(optional_param)
    return necessary_param

def main():
    print_spider()
    try:
        params_dict = cmd_parse()
    except FilePathInvalid as msg:
        log.error(msg)
    else:
        config_path = params_dict.get('config')
        # default 2 minutes.
        timer = int(params_dict.get('timer', 2))
        # default 5 threads.
        max_workers = int(params_dict.get('max_workers', 5))

        collector = list()
        futures_map = dict()
        config = Config(config_path)
        devices_list = list()
        platform = config.platformName
        if platform == 'Android':
            devices_list = get_serial_numbers_android()
        elif platform == 'iOS':
            devices_list = get_serial_numbers_ios()
        else:
            log.error("Not support {} platform".format(platform))

        if not devices_list:
            log.warning("Not find any device.")
        else:
            with futures.ThreadPoolExecutor(max_workers) as executor:
                futures_list = []
                for serial in devices_list:
                    future = executor.submit(performer, config_path, serial, timer)
                    futures_map[future] = serial
                    futures_list.append(future)

                for future in futures.as_completed(futures_list):
                    print(futures_map.get(future))
                    report_dir, record = future.result()
                    json_gene = GenerateJson(report_dir, record)
                    json_gene.insert_crash_log()
                    json_gene.generate_json()

                    # generate report
                    report = Report(report_dir=report_dir)
                    report.clear_expired_report(expired_day=3)
                    report.generate_report()

            kill_adb_server()
            log.warning("All test end.")


if __name__ == '__main__':
    main()



