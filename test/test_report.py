#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/21
import os

from report_util import Report

class TestReport:

    def setup(self):
        print("test start.")
        report_dir = os.path.join(os.path.dirname(__file__), '..', 'reports', 'test')
        self.report = Report(report_dir=report_dir)

    def teardown(self):
        print("test end.")

    def test_generate_report(self):
        self.report.generate_report()

    def test_clear_reort(self):
        self.report.clear_expired_report(3)

