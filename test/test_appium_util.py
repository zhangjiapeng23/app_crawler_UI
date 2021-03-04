#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10
import os
import time

from config_util import Config
from appium_util import Appium
import device_info_util

class TestAppiumUtil:

    def setup(self):
        print('Test start.')
        # config_path = '/Users/jameszhang/python/project/appCrawler/test/testdata/config/NBA_Android_config.yml'
        config_path = os.path.join(os.path.dirname(__file__), 'testdata/config', 'NBA_Android_config.yml')
        uid = device_info_util.get_serial_numbers_android()
        self.config = Config(config_path, uid[0])

    def teardown(self):
        print('Test end.')
        del self.config

    def test_appium_init_driver(self):
        self.driver = Appium(self.config.appium_desired_caps())
        self.driver.quit()

    def test_save_page_source(self):
        self.driver = Appium(self.config.appium_desired_caps())
        time.sleep(20)
        page_source = self.driver.get_page_source()
        date = str(int(time.time()))
        with open('testdata/pageSource/{}.xml'.format(date), 'w', encoding='utf-8') as fp:
            fp.write(page_source)

        self.driver.quit()





