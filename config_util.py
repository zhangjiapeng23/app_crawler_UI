#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10

import os
import re
from collections import defaultdict

import yaml

import device_info_util


class Config:
    """
    params:
        config: config file absolute path
    """

    def __init__(self, config_path: str, udid=None):
        self.__udid = udid
        self.__config_path = config_path
        if not os.path.isfile(self.__config_path):
            raise Exception("Not find a invalid file.")

        if not self.__config_path.endswith(('.yml', '.yaml')):
            file_format = re.match(r'.*(\..*)', self.__config_path)[1]
            e_msg = "Only support yaml format config, your config is {} format."
            raise Exception(e_msg.format(file_format))

        with open(self.__config_path, 'r', encoding='utf-8') as f:
            self.__config = yaml.safe_load(f)

    def __repr__(self):
        return type(self).__name__ + '("{}")'.format(self.__config_path)

    def __getattr__(self, item):
        if item in self.__config.keys():
            return self.__config[item]
        else:
            e_msg = "{} object has no attribute '{}'".format(type(self).__name__, item)
            raise AttributeError(e_msg)

    @property
    def config(self):
        return self.__config

    @property
    def udid(self):
        return self.__udid

    def appium_desired_caps(self):
        desired_caps = defaultdict(lambda: None)
        desired_caps['platformName'] = self.config.get('platformName')
        desired_caps['appiumServerUrl'] = self.config.get('appiumServerUrl')
        desired_caps['port'] = self.config.get("appiumPort")
        desired_caps['app'] = self.config.get('app')
        desired_caps['noReset'] = self.config.get("noReset")
        desired_caps['autoGrantPermissions'] = self.config.get('autoGrantPermissions')
        # desired_caps['dontStopAppOnReset'] = 'true'
        desired_caps['skipDeviceInitialization'] = 'true'
        desired_caps['unicodeKeyBoard'] = 'true'
        desired_caps['resetKeyBoard'] = 'true'

        if desired_caps['platformName'] == 'Android':
            desired_caps['deviceName'] = device_info_util.get_device_name_android(self.__udid)
            desired_caps['platformVersion'] = device_info_util.get_device_system_version_android(self.__udid)
            desired_caps['appPackage'] = self.config.get('appPackage')
            desired_caps['appActivity'] = self.config.get('appActivity')
            desired_caps['automationName'] = self.config.get('automationName')

        else:
            # desired['deviceName'] = device_info.get_device_name_ios(udid)
            # desired['platformVersion'] = device_info.get_device_system_version_ios(udid)
            # desired['wdaLocalPort'] = self.config_dic.get('WDAbundleId')
            # desired['bundleId'] = self.config_dic.get('bundleId')
            # Simulator
            udid = "D74E2A22-237D-4653-A63C-5B9C40B5A747"
            desired_caps['deviceName'] = 'iphone 11 pro Max'
            desired_caps['platformVersion'] = device_info_util.get_device_system_version_ios(udid)
            desired_caps['bundleId'] = self.config.get('bundleId')
            desired_caps['WDAbundleId'] = 'com.apple.test.WebDriverAgentRunner-Runner'
            desired_caps['wdaLocalPort'] = 8200
        desired_caps['udid'] = self.__udid
        return desired_caps

    def white_apps(self) -> set:
        white_apps = self.config.get("whiteApps", list())
        return set(white_apps)

    def last_elements(self) -> set:
        last_elements = self.config.get("lastElements", list())
        return set(last_elements)

    def black_elements(self) -> set:
        black_elements = self.config.get("blackElements", list())
        return set(black_elements)

    def white_elements(self) -> set:
        white_elements = self.config.get("whiteElements", list())
        return set(white_elements)

    def black_activities(self) -> set:
        black_activities = self.config.get("blackActivities", list())
        return set(black_activities)

    def base_activities(self) -> set:
        base_activities = self.config.get("baseActivities", list())
        return set(base_activities)

    def selected_elements(self) -> set:
        selected_elements = self.config.get("selectedElements", list())
        if not selected_elements:
            # set default
            selected_elements = ['.*Text.*', '.*Image.*', '.*Button.*', '.*CheckBox.*']
        return selected_elements
