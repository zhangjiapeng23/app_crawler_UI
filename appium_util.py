#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10
import base64
import random

import cv2
import numpy as np
from appium import webdriver
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException

from log import log


class Appium:

    def __init__(self, desired_caps):
        appium_server_url = desired_caps['appiumServerUrl'] if desired_caps['appiumServerUrl'] else "http://127.0.0.1"
        appium_server_url += ':{}/wd/hub'.format(desired_caps['port'])
        self.__driver = webdriver.Remote(appium_server_url, desired_caps)

    @property
    def driver(self):
        return self.__driver

    def scroll_up_page(self, duration=400):
        screen_size = self.__driver.get_window_size()
        x_start = x_end = screen_size['width'] / 2
        y_start = screen_size['height'] * 0.80
        y_end = screen_size['height'] * 0.30
        try:
            self.__driver.swipe(start_x=x_start, end_x=x_end, start_y=y_start, end_y=y_end, duration=duration)
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Swipe action cannot be performed! {}".format(err))

    def scroll_down_page(self, duration=400):
        screen_size = self.__driver.get_window_size()
        x_start = x_end = screen_size['width'] / 2
        y_end = screen_size['height'] * 0.70
        y_start = screen_size['height'] * 0.30
        try:
            self.__driver.swipe(start_x=x_start, end_x=x_end, start_y=y_start, end_y=y_end, duration=duration)
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Swipe action cannot be performed! {}".format(err))

    def pull_refresh_page(self):
        self.scroll_down_page()
        log.info("Pull refresh page!")

    def load_long_page_content(self, times=1):
        for i in range(times):
            self.scroll_up_page()
        log.info("Scroll down page to show more content!!")

    def monkey_tap(self, duration=400):
        screen_size = self.__driver.get_window_size()
        positions = []
        width = screen_size['width']
        height = screen_size['height']
        for i in range(5):
            x = random.randint(0, width)
            y = random.randint(100, height)
            position = (x, y)
            positions.append(position)
        try:
            # click event
            self.__driver.tap(positions=positions, duration=duration)
            log.info("random swipe click!")
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Click action cannot be performed! {}".format(err))

    def monkey_swipe_left(self, duration=400):
        screen_size = self.__driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        x = random.randint(0, width)
        x_end = random.randint(0, x)
        y = random.randint(100, height)
        try:
            # swipe left event
            self.__driver.swipe(start_x=x, start_y=y, end_x=x_end, end_y=y, duration=duration)
            log.info("random swipe left!")
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Swipe action cannot be performed! {}".format(err))

    def monkey_swipe_right(self, duration=400):
        screen_size = self.__driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        x = random.randint(0, width)
        x_end = random.randint(x, width)
        y = random.randint(100, height)
        try:
            # swipe left event
            self.__driver.swipe(start_x=x, start_y=y, end_x=x_end, end_y=y, duration=duration)
            log.info("random swipe right!")
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Swipe action cannot be performed! {}".format(err))

    def monkey_swipe_up(self, duration=400):
        screen_size = self.__driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        x = random.randint(0, width)
        y = random.randint(100, height)
        y_end = random.randint(100, y)
        try:
            self.__driver.swipe(start_x=x, start_y=y, end_x=x, end_y=y_end, duration=duration)
            log.info("random swipe up!")
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Swipe action cannot be performed! {}".format(err))

    def monkey_swipe_down(self, duration=400):
        screen_size = self.__driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        x = random.randint(0, width)
        # avoid swipe top system box, not from 0 start.
        y = random.randint(100, height)
        y_end = random.randint(y, height)
        try:
            self.__driver.swipe(start_x=x, start_y=y, end_x=x, end_y=y_end, duration=duration)
            log.info("random swipe down!")
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Swipe action cannot be performed! {}".format(err))

    def monkey_app_background(self):
        time = random.randint(3, 10)
        log.info("Put app to background {} seconds.".format(time))
        try:
            self.__driver.background_app(time)
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error(err)

    def monkey_actions(self):
        # trigger random actions probability.
        execute = random.randint(0, 5)
        if execute == 1:
            event = random.randint(0, 7)
            if event == 0 or event == 1:
                self.monkey_tap()
            if event == 1:
                self.monkey_swipe_up()
            if event == 2 or event == 3 or event == 7:
                self.monkey_swipe_down()
            if event == 3 or event == 4:
                self.monkey_swipe_left()
            if event == 4 or event == 5:
                self.monkey_swipe_right()
            if event == 6:
                self.monkey_app_background()

    @staticmethod
    def screenshot_mark(img_path: str, position: tuple):
        index = img_path.rfind(".png")
        new_img_path = img_path[:index] + "_click.png"
        rimg = cv2.imread(img_path)
        cv2.rectangle(rimg, position[0], position[1], (0, 0, 255), 5)
        cv2.imwrite(new_img_path, rimg)

    def save_screenshot(self, path: str, position: tuple):
        try:
            self.__driver.get_screenshot_as_file(path)
            self.screenshot_mark(img_path=path, position=position)
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Screenshot failed! {}".format(err))

    def save_screenshot_as_base64(self, position=None):
        try:
            origin = self.__driver.get_screenshot_as_base64()
            if position:
                origin = self.screenshot_mark_as_base64(origin, position)
            return origin
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Screenshot failed! {}".format(err))

    @staticmethod
    def screenshot_mark_as_base64(base64_encode, position):
        base64_decode = base64.b64decode(base64_encode)
        nparr = np.fromstring(base64_decode, np.uint8)
        image = cv2.imdecode(nparr, cv2.COLOR_BGR2RGB)
        cv2.rectangle(image, position[0], position[1], (0, 0, 255), 5)
        base64_str = cv2.imencode('.jpg', image)[1].tostring()
        base64_str = base64.b64encode(base64_str)
        return base64_str



    def launch_app(self):
        try:
            self.__driver.launch_app()
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error('Launch app error! {}'.format(err))

    def get_current_activity(self):
        for count in range(3):
            try:
                current_activity = self.__driver.current_activity
            except InvalidSessionIdException as err:
                raise err
            except WebDriverException as err:
                log.error("get activity error! {}".format(err))
                current_activity = None
            if current_activity is not None:
                return current_activity
        else:
            log.warning("Get activity timeout!!!")
            return ''

    def get_page_source(self):
        try:
            return self.__driver.page_source
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Get current page source error! {}".format(err))

    def get_current_package(self):
        for count in range(3):
            try:
                current_package = self.__driver.current_package
            except InvalidSessionIdException as err:
                raise err
            except WebDriverException as err:
                log.error("Get package error!! {}".format(err))
                current_package = None
            if current_package is not None:
                return current_package
        else:
            log.warning("Get package timeout!!!")
            return ''

    def click_device_back(self):
        try:
            # self.__driver.keyevent(4)
            # self.__driver.back()
            self.__driver.press_keycode(4)
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Click device back button error! {}".format(err))

    def find_elements(self, xpath):
        elements = []
        try:
            elements = self.__driver.find_elements_by_xpath(xpath)
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Find element error! {}".format(err))
        finally:
            return elements

    def quit(self):
        try:
            self.__driver.quit()
            log.info("Clear this test session!")
        except InvalidSessionIdException as err:
            raise err
        except WebDriverException as err:
            log.error("Quit session error! {}".format(err))



