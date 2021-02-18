#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10
import base64
import os
import time

from appium_util import Appium
from config_util import Config
import device_info_util

class TestScreenShot:

    def setup(self):
        print('test start')
        uid = device_info_util.get_serial_numbers_android()
        config = Config('E:\\app_crawler_UI\\test\\testdata\\config\\NBA_Android_config.yml', uid[0])
        self.driver = Appium(config.appium_desired_caps())

    def teardown(self):
        self.driver.quit()
        print('Test end')

    def test_screenshot_as_base64(self):
        res = self.driver.save_screenshot_as_base64()
        png = base64.b64decode(res.encode('ascii'))
        path = os.path.join(os.path.dirname(__file__), 'testdata\\screenshot', str(int(time.time())) + '.png')
        with open(path, 'wb') as f:
            f.write(png)

    def test_screenshot_mark_as_base64(self):
        position = [(200, 200), (100, 100)]
        orgin_base64 = self.driver.save_screenshot_as_base64()
        res =self.driver.screenshot_mark_as_base64(orgin_base64, position)
        print(res)
        png = base64.b64decode(res)
        path = os.path.join(os.path.dirname(__file__), 'testdata\\screenshot', str(int(time.time())) + '.png')
        with open(path, 'wb') as f:
            f.write(png)





