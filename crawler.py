#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10
import datetime
import os
import time
from collections import deque, namedtuple
import re
from random import random

from func_timeout import func_set_timeout
from func_timeout.exceptions import FunctionTimedOut
from selenium.common.exceptions import WebDriverException

from page_parse import PageParse
from config_util import Config
from appium_util import Appium
from xpath_util import XpathParseIteration, ElementUid
from log import log
from report_util import LogAndroid


class Crawler:
    event_record = namedtuple('event', ['time', 'before_click', 'after_click', 'activity', 'xpath', 'status',
                                        'element_uid'])
    travel_mode = None

    def __init__(self, config: Config, timer):
        self._start_time = datetime.datetime.now()
        XpathParseIteration.travel_mode = self.travel_mode
        self.max_page_depth = config.config.get('max_depth', 6)
        crash_traceback = config.config.get('max_screen')
        self.__crash_traceback = deque(maxlen=crash_traceback) if crash_traceback else deque(maxlen=10)
        self.seen = set()
        self.__config = config
        self.white_apps = self.__config.white_apps()
        self.black_elements = self.__config.black_elements()
        self.black_activities = self.__config.black_activities()
        self.white_elements = self.__config.white_elements()
        self.base_activities = self.__config.base_activities()
        self.last_elements = self.__config.last_elements()
        self.first_elements = self.__config.first_elements()
        self.selected_elements = self.__config.selected_elements()
        self.after_crawl_page = self.__config.after_crawl_page()
        self.driver = None
        self.init_appium()
        self.__current_page = None
        self.__record = list()
        self.__timer = timer * 60
        log.info("Total time: {} seconds".format(self.__timer))
        self.__white_element_seen = set()

        # init device crash log, remove cache crash log.
        self.android_log = LogAndroid(udid=self.__config.udid)
        self.android_log.clear_log()

        # init report
        report_dir = os.path.join(os.path.dirname(__file__), 'reports')
        if not os.path.exists(report_dir):
            os.mkdir(report_dir)
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.__report_path = os.path.join(report_dir, current_time + '_' + self.__config.udid)
        os.mkdir(self.__report_path)
        self.__screenshot_dir = os.path.join(self.__report_path, 'screenshot')
        os.mkdir(self.__screenshot_dir)

    def __call__(self):
        self.run()

    def __repr__(self):
        return '<{0!r}: {1!r}>'.format(type(self).__name__, self.__config.projectName)

    @func_set_timeout(5)
    def __get_page_source(self):
        if self._start_time + datetime.timedelta(seconds=self.timer) <= datetime.datetime.now():
            self.quit()
        return self.driver.get_page_source()

    def init_appium(self):
        self.driver = Appium(desired_caps=self.__config.appium_desired_caps())

    def get_page_source(self):
        count = 2
        while count:
            try:
                # globally unique refresh __current_page. make sure record newest page info.
                self.__current_page = self.__get_page_source()
                return self.__current_page
            except FunctionTimedOut:
                count -= 1
            except WebDriverException as e:
                log.error(e)
                log.warning('refresh appium driver')
                self.init_appium()
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
            # test: if after click back, still timeout, relaunch app.
            try:
                self.__get_page_source()
            except FunctionTimedOut:
                self.driver.launch_app()
                log.warning('Get page source timeout, relaunch app.')
            except WebDriverException:
                log.warning('refresh appium driver')
                self.init_appium()
            finally:
                return self.get_page_info()
        else:
            current_activity = self.driver.get_current_activity()
            page = PageParse(current_page_source, current_activity)
            return page

    def run(self):
        '''
        page crawl main control center.
        '''
        page_stack = deque()
        # page_stack: type: list, save wait to crawl page xml data.
        # call get_page_info to get current page xml and put to list.
        page_stack.append(self.get_page_info())

        while page_stack:
            # pop list top one to start crawl
            page = page_stack.pop()
            # check this page is the same as current_page
            if page == self.__current_page:
                # call crawl_page method to start click this page.
                crawl_gen = self.crawl_page(page)
                for res in crawl_gen:
                    if res != 'END':
                        if self.__is_base_activity(self.driver.get_current_activity()):
                            page_stack.clear()
                            page_stack.append(res[0])
                            break
                        else:
                            # check current page stack depth is whether or not more then max_page_depth
                            if len(page_stack) >= self.max_page_depth:
                                # click back
                                log.warning('Current page deep is more than max depth, click back.')
                                self.driver.click_device_back()
                                continue
                            else:
                                # put current page into stack
                                page_stack.append(res[1])
                                # put new page into stack
                                page_stack.append(res[0])
                                break
                    else:
                        # end this page crawl
                        break

    def crawl_page(self, xpath_generator):
        '''
            Need received a XpathParse instance.
            xpath_generator: XpathParse instance.
        '''
        if not isinstance(xpath_generator, XpathParseIteration):
            # if not a XpathParse instance, try to structure a XpathParse instance.
            self.__xpath_generator = XpathParseIteration(xpath_generator,
                                                         first_elements_config=self.first_elements,
                                                         last_elements_config=self.last_elements)
        else:
            self.__xpath_generator = xpath_generator

        for xpath, node_uid in self.__xpath_generator:
            if not self.__before_click(node_uid):
                continue

            res = self.__click(xpath, node_uid)

            # if res not None, represent page change, return to run,
            # else click next one
            if res is not None:
                yield res

        else:
            # when all page elements is clicked. trigger after crawl page event.
            # self.driver.load_long_page_content(times=2)
            # self.driver.pull_refresh_page()
            self.__after_crawl_page()

            current_page = self.get_page_info()
            if current_page != self.__xpath_generator:
                yield current_page, self.__xpath_generator

        log.debug("Current page crawler over!")
        if not self.__is_base_activity(self.driver.get_current_activity()):
            self.driver.click_device_back()
        else:
            log.warning("Current page is base activity.")
        yield 'END'

    def __before_click(self, node_uid: ElementUid):
        # check the node whether has been clicked
        if node_uid.uid in self.seen:
            # log.info('element {} is seen, skip it.'.format(node_uid.uid))
            return 0
        # check the node whether is in white list seen
        # prevent always click white element.
        if node_uid.uid in self.__white_element_seen:
            # generate a random number to decide this node remove from seen.
            if random() <= 0.3:
                self.__white_element_seen.remove(node_uid.uid)
                log.info('Remove an element from white seen.')
            return 0
        # check the node whether is in selected list.
        if not self.__is_selected_element(node_uid.uid):
            # log.warning("Current element not in selected list, not click.\n{}".format(node_uid.uid))
            self.seen.add(node_uid.uid)
            return 0
        # check the node whether is in black list.
        if self.__is_black_element(node_uid.uid):
            log.warning("Current element in black list, not click. {}.".format(node_uid.uid))
            self.seen.add(node_uid.uid)
            return 0
        return 1

    def __click(self, xpath, node_uid: ElementUid):
        if xpath != '' and xpath[-1] != '*':
            elements = self.driver.find_elements(xpath)
            if len(elements) > 0:
                # record before click screenshot
                screenshot_before_click = self.driver.save_screenshot_as_jpg(self.__screenshot_dir, node_uid.bounds)

                try:
                    elements[0].click()
                except Exception as err:
                    log.error("element click error! {}".format(err))
                    return None
                else:
                    # record after click screenshot
                    screenshot_after_click = self.driver.save_screenshot_as_jpg(self.__screenshot_dir)

                    # log.error("click a element! Path: {}".format(xpath))

                    # recode click event info.
                    self.__statistics(xpath, node_uid.uid, screenshot_before_click, screenshot_after_click)

                    if not self.__is_white_element(node_uid.uid):
                        self.seen.add(node_uid.uid)
                    else:
                        # add to white element seen set
                        self.__white_element_seen.add(node_uid.uid)

                    # add random actions
                    self.driver.monkey_actions()

                    self.__after_click()
                    # judge page is change
                    current_page = self.get_page_info()
                    if current_page != self.__xpath_generator:
                        return current_page, self.__xpath_generator
                    else:
                        return None
            else:
                return None

    def __after_click(self):
        # check is in black activity
        if self.__is_black_activity(self.driver.get_current_activity()):
            self.driver.click_device_back()
        else:
            self.__return_white_app()

    def __after_crawl_page(self):
        for event in self.after_crawl_page:
            try:
                action = getattr(self.driver, event.get('name', 'None'))
            except AttributeError as exc:
                log.error(f"Not support {event.get('name', 'None')} event, {exc}")
            else:
                for _ in range(event.get('times', 0)):
                    action()

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

    def __is_selected_element(self, node_uid):
        return self.__re_search(node_uid, self.selected_elements)

    @staticmethod
    def __re_search(target, _list):
        for item in _list:
            if re.search(r'{}'.format(item), target):
                return True
        return False

    def __statistics(self, xpath, node_uid,
                     screenshot_before_click, screenshot_after_click):
        node_uid_split = node_uid.split(':')
        activity = node_uid_split[0]
        element_uid = ''.join(node_uid_split[1:])
        event = self.event_record(time=int(time.time()),
                                  before_click=screenshot_before_click,
                                  after_click=screenshot_after_click,
                                  activity=activity,
                                  xpath=xpath,
                                  status='pass',
                                  element_uid=element_uid)
        self.__record.append(event)

    @property
    def timer(self):
        return self.__timer

    def quit(self):
        log.warning('Appium quit')
        self.driver.quit()

    @property
    def record(self):
        self.android_log.collect_log(self.report_path)
        return self.__record

    @property
    def report_path(self):
        return self.__report_path













