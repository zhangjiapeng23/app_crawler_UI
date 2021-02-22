#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10
import os

from report_util import GenerateJson
from crawler import Crawler


class TestGenerateJson:

    def setup(self):
        print('test start.')
        self.record = []
        for i in range(0, 50000, 100):
            self.record.append(Crawler.event_record(1611900545+i, 'test', 'test', 'test', 'test', 'pass'))
        log_path = os.path.join(os.path.dirname(__file__), 'testdata/log/nba_crash.log')
        self.gen_js = GenerateJson(log_path=log_path, record=self.record)

    def teardown(self):
        print('test end.')

    def test_crash_log(self):
        self.gen_js.extract_crash_log()
        print(self.gen_js.crash_log)

    def test_insert_log(self):
        self.gen_js.extract_crash_log()
        self.gen_js.insert_crash_log()
        for i in self.record:
            print(i)
            print('='*20)


