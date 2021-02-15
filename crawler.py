#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10

from collections import deque, defaultdict
import re

from func_timeout import func_set_timeout
from func_timeout.exceptions import FunctionTimedOut

from page_parse import PageParse
from config_util import Config
from appium_util import Appium
from xpath_util import XpathParse
from log import log


class Crawler:

    def __init__(self, config: Config, timer=1):
        max_page_depth = config.config.get('max_depth')
        self.page_stack = deque(maxlen=max_page_depth) if max_page_depth else deque(maxlen=3)
        self.seen = set()
        self.__config = config
        self.white_apps = self.__config.white_apps()
        self.black_elements = self.__config.black_elements()
        self.black_activities = self.__config.black_activities()
        self.white_elements = self.__config.white_elements()
        self.base_activities = self.__config.base_activities()
        self.last_elements = self.__config.last_elements()
        self.driver = Appium(desired_caps=config.appium_desired_caps())
        self.__current_page = None
        self.__record = defaultdict(list)
        self.__timer = timer

    def __call__(self):
        self.run()

    def __repr__(self):
        return '{}<{}>'.format(type(self).__name__, self.__config.projectName)

    @func_set_timeout(5)
    def __get_page_source(self):
        return self.driver.get_page_source()

    def get_page_source(self):
        count = 2
        while count:
            try:
                self.__current_page = self.__get_page_source()
                return self.__current_page
            except FunctionTimedOut:
                count -= 1
        log.error('Get page source timeout.')
        return None

    def get_page_info(self):
        '''
        Returns:
            page: PageParse class instance.
            current_activity: string
        '''
        current_page_source = self.get_page_source()
        if not current_page_source:
            self.driver.click_device_back()
            return self.get_page_info()
        else:
            current_activity = self.driver.get_current_activity()
            page = PageParse(current_page_source, current_activity)
            return page

    def run(self):
        if not self.page_stack:
            self.page_stack.append(self.get_page_info())

        while self.page_stack:
            page = self.page_stack.pop()
            if page == self.__current_page:
                res = self.crawl_page(page)
                if res != 'END':
                    if self.__is_base_activity(res[0].current_activity):
                        self.page_stack.clear()
                    else:
                        # put current page into stack
                        self.page_stack.append(res[1])
                    # put new page into stack
                    self.page_stack.append(res[0])

    def crawl_page(self, xpath_generator):
        if not isinstance(xpath_generator, XpathParse):
            self.__xpath_generator = XpathParse(xpath_generator, self.seen)
        else:
            self.__xpath_generator = xpath_generator

        for xpath, node_uid in self.__xpath_generator:
            if node_uid in self.seen:
                log.info('element {} is seen, skip it.'.format(node_uid))
                continue
            elif self.__is_black_element(xpath):
                log.warning("Current element in black list, not click.")
                self.seen.add(node_uid)
                continue
            elif self.__is_last_element(xpath):
                log.warning("Current element in last list, check later.")
                self.__xpath_generator.last.append((xpath, node_uid))
                continue
            else:
                res = self.__click(xpath, node_uid)
                if res:
                    return res

        else:
            for xpath, node_uid in self.__xpath_generator.last:
                res = self.__click(xpath, node_uid)
                if res:
                    return res
            else:
                self.driver.load_long_page_content(times=2)
                self.driver.pull_refresh_page()
                current_page = self.get_page_info()
                if current_page != self.__xpath_generator:
                    return current_page, self.__xpath_generator

        log.debug("Current page crawler over!")
        if not self.__is_base_activity(self.driver.get_current_activity()):
            self.driver.click_device_back()
        else:
            log.warning("Current page is base activity.")
        return 'END'

    def __click(self, xpath, node_uid):
        if xpath != '' and xpath[-1] != '*':
            elements = self.driver.find_elements(xpath)
            if len(elements) > 0:
                try:
                    elements[0].click()
                except Exception as err:
                    log.error("element click error! {}".format(err))
                else:
                    # log.error("click a element! Path: {}".format(xpath))
                    self.__statistics(xpath, node_uid)

                    if not self.__is_white_element(node_uid):
                        self.seen.add(node_uid)

                        # add random actions
                        self.driver.monkey_actions()

                        self.__after_click()

                        # judge page is change
                        current_page = self.get_page_info()
                        if current_page != self.__xpath_generator:
                            return current_page, self.__xpath_generator

    def __after_click(self):
        # check is in black activity
        if self.__is_black_activity(self.driver.get_current_activity()):
            self.driver.click_device_back()
        else:
            self.__return_white_app()

    def __return_white_app(self):
        for count in range(3):
            current_package = self.driver.get_current_package()
            if self.__is_white_app(current_package):
                break
            else:
                log.info('current app is not white app!')
                self.driver.click_device_back()
        else:
            log.info('relaunch test app!!')
            self.driver.launch_app()

    def __is_base_activity(self, activity):
        return self.__re_search(activity, self.base_activities)

    def __is_white_element(self, node_uid):
        return self.__re_search(node_uid, self.white_elements)

    def __is_black_element(self, node_uid):
        return self.__re_search(node_uid, self.black_elements)

    def __is_last_element(self, node_uid):
        return self.__re_search(node_uid, self.last_elements)

    def __is_white_app(self, app):
        return self.__re_search(app, self.white_apps)

    def __is_black_activity(self, activity):
        return self.__re_search(activity, self.black_activities)

    @staticmethod
    def __re_search(target, _list):
        for item in _list:
            if re.search(r'{}'.format(item), target):
                return True
        return False

    def __statistics(self, xpath, node_uid):
        activity = node_uid.split(':')[0]
        self.__record[activity].append(xpath)

    @property
    def timer(self):
        return self.__timer

    def quit(self):
        for key in self.__record.keys():
            msg = 'activity: {}, total: {}, path: {}'
            print(msg.format(key, len(self.__record[key]), self.__record[key]))
        self.driver.quit()














