#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10
import os
import time

from report_util import LogAndroid
from device_info_util import get_serial_numbers_android

class TestAndroidLog:

    def setup(self):
        print('test start!')
        udid = get_serial_numbers_android()[0]
        self.log = LogAndroid(udid)
        self.log.clear_log()

    def teardown(self):
        print('test end!')

    def test_save_log(self):
        time.sleep(10)
        report_path = os.path.join(os.path.dirname(__file__), 'test/testdata/log')
        self.log.collect_log(report_path)



