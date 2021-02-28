#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/21

from report_util import Report

class TestReport:

    def setup(self):
        print("test start.")
        self.report = Report(report_name='james_test_2')

    def teardown(self):
        print("test end.")

    def test_generate_report(self):
        self.report.generate_report()

