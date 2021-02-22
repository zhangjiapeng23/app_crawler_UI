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
        config_path = os.path.join(os.path.dirname(__file__),
                                   'testdata', 'config', 'NBA_Android_config.yml')
        config = Config(config_path, uid[0])
        screenshot = os.path.join(os.path.dirname(__file__), 'testdata\\screenshot')
        if not os.path.exists(screenshot):
            os.mkdir(screenshot)
        self.driver = Appium(config.appium_desired_caps())

    def teardown(self):
        self.driver.quit()
        print('Test end')

    def test_screenshot_as_base64(self):
        res = self.driver.save_screenshot_as_base64()
        res = base64.b64decode(res)
        print(res[:10])
        path = os.path.join(os.path.dirname(__file__), 'testdata\\screenshot', str(int(time.time())) + '.jpg')
        with open(path, 'wb') as f:
            f.write(res)

    def test_screenshot_mark_as_base64(self):
        position = [(200, 200), (100, 100)]
        res =self.driver.save_screenshot_as_base64(position)
        res = base64.b64decode(res)
        print(res[:10])
        path = os.path.join(os.path.dirname(__file__), 'testdata\\screenshot', str(int(time.time())) + '.jpg')
        with open(path, 'wb') as f:
            f.write(res)

    def test_screenshot_as_jpg(self):
        path = os.path.join(os.path.dirname(__file__), 'testdata\\screenshot')
        res = self.driver.save_screenshot_as_jpg(screenshot_dir=path)
        print(res)

    def test_screenshot_mark_as_jpg(self):
        position = [(200, 200), (100, 100)]
        path = os.path.join(os.path.dirname(__file__), 'testdata\\screenshot')
        res = self.driver.save_screenshot_as_jpg(screenshot_dir=path, position=position)
        print(res)



