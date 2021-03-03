#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/3/3
import sys
import os

from startup import cmd_parse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class CmdPars:

    def setup_method(self):
        print('test start.')

    def teardown_method(self):
        print('test end.')

    def test_cmd_parse(self):
        cmd_parse()

if __name__ == '__main__':
    cmd_parse()