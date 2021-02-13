#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10
import threading

from selenium.common.exceptions import InvalidSessionIdException

from crawler import Crawler
from config_util import Config
from log import log


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


if __name__ == '__main__':
    print_spider()
    config = Config('config/NBA_Android_config.yml')
    spider = Crawler(config, 2)
    execute_timer(spider.timer, spider.quit)
    try:
        while True:
            spider.run()
    except InvalidSessionIdException:
        log.error('test end!')

