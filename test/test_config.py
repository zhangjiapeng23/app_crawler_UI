#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10

from collections.abc import Set

import pytest

from config_util import Config


class TestConfigInit:

    def setup(self):
        print('Test start')

    def teardown(self):
        print('Test end')

    @pytest.mark.parametrize('path',
                             ['/Users/jameszhang/python/project/appCrawler/test/testdata/config/NBA_Android_config.yaml',
                              '/Users/jameszhang/python/project/appCrawler/test/testdata/config/NBA_Android_config.yml'],
                             ids=['correct_yaml', 'correct_yml'])
    def test_config_file_correct(self, path):
        Config(path)

    @pytest.mark.parametrize('path',
                             ['/Users/jameszhang/python/project/appCrawler/test/testdata/config/NBA_Android_config_1.yaml',
                              '/Users/jameszhang/python/project/appCrawler/test/testdata/config/',
                              '/Users/jameszhang/python/project/appCrawler/test/testdata/config/NBA_Android_config.json'],
                             ids=['no exist', 'not file', 'incorrect format'])
    def test_config_file_incorrect(self, path):
        with pytest.raises(expected_exception=Exception):
            Config(path)


class TestConfigData:

    def setup(self):
        print('Test start.')
        self.config = Config('/Users/jameszhang/python/project/appCrawler/test/testdata/config/NBA_Android_config.yml')

    def teardown(self):
        del self.config
        print('Test end.')

    def test_get_attr_str(self):
        platform_name = self.config.platformName
        assert platform_name == 'Android'

    def test_get_attr_list(self):
        list_data = self.config.test_list
        for i in range(1, 4):
            assert list_data[i-1] == i

    def test_get_attr_error(self):
        with pytest.raises(expected_exception=AttributeError):
            self.config.error_attr

    def test_get_appium_desired_caps(self):
        desired_caps = self.config.appium_desired_caps()
        assert desired_caps['appPackage'] == 'com.nbaimd.gametime.nba2011'
        assert desired_caps['appActivity'] == 'com.neulion.nba.base.LaunchDispatcherActivity'

    def test_white_apps(self):
        white_apps = self.config.white_apps()
        assert isinstance(white_apps, Set)
        assert "com.nbaimd.gametime.nba2011" in white_apps






