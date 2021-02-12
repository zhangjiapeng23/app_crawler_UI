#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10

import logging


class Log:

    def __init__(self):
        self.logger = logging.getLogger()

    def error(self, message):
        self.warning(message)
        # self.logger.error(message)

    def debug(self, message):
        self.logger.warning(message)
        # self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def info(self, message):
        self.warning(message)
        # self.logger.info(message)


log = Log()
