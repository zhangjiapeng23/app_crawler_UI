#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10

from collections.abc import Sequence

from device_info_util import get_serial_numbers_android

class TestDeviceUtil:

    def setup(self):
        print('Test start.')

    def teardown(self):
        print('Test end.')

    def test_serial_numbers_android(self):
        res = get_serial_numbers_android()
        print(res)
        assert isinstance(res, Sequence)
        assert len(res) >= 0


