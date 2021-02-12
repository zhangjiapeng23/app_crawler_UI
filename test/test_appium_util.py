#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10

from config_util import Config
from appium_util import Appium

class TestAppiumUtil:

    def setup(self):
        print('Test start.')
        config_path = '/Users/jameszhang/python/project/appCrawler/test/testdata/config/NBA_Android_config.yml'
        self.config = Config(config_path)

    def teardown(self):
        print('Test end.')
        del self.config

    def test_appium_init_driver(self):
        self.driver = Appium(self.config.appium_desired_caps())
        self.driver.driver.quit()

