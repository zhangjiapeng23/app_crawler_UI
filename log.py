#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10

import logging
import os
import time

def singleton(cls):
    _instance = {}

    def inner(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return inner

@singleton
class Log:

    def __init__(self):
        self.logger = logging.getLogger('AppCrawler')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        filename = time.strftime('%Y%m%d_%H%M%S') + '_log.log'
        file_path = os.path.join(log_dir, filename)
        fh = logging.FileHandler(filename=file_path, encoding='utf-8')
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        text = "=" * 10 + time.strftime('%H:%M:%S') + "=" * 10
        self.info(text)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def info(self, message):
        self.logger.info(message)


log = Log()
