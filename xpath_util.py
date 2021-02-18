#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10
import re
import uuid
from collections import deque


class XpathParse:

    def __init__(self, page, seen):
        self.__routing = {}
        self.__direct_routing = {}
        self.__stack = deque()
        self.__page = page
        self.__root = self.__page()
        # each node will be key of routing map, add attr uuid to keep unique.
        self.__root.set('uuid', str(uuid.uuid1()))
        self.__stack.append(self.__root)
        # root parent node is None
        self.__routing[self.__root] = None
        self.seen = seen
        self.last = []

    def __eq__(self, other):
        return self.__page == other

    def __iter__(self):
        return self

    def __next__(self):
        err = None
        try:
            node = self.__stack.pop()
        except IndexError as e:
            err = e
        finally:
            if err:
                raise StopIteration(err)
            else:
                for child in node:
                    child.set('uuid', str(uuid.uuid1()))
                    self.__stack.append(child)
                    self.__routing[child] = node
                return self.xpath(node)

    def xpath(self, node):
        node_xpath = ''
        # node_uid = self.generate_element_uid(node.attrib)
        node_uid = ElementUid(node_attrib=node.attrib, activity=self.__page.current_activity)
        if node_uid.uid not in self.seen:
            v_node = node
            while v_node is not None:
                if v_node in self.__direct_routing.keys():
                    node_xpath = self.__direct_routing[v_node] + node_xpath
                    break

                xpath = self.xpath_parsing(v_node)
                if xpath is not None:
                    node_xpath = '//' + xpath + node_xpath
                else:
                    break

                v_node = self.__routing[v_node]
            self.__direct_routing[node] = node_xpath
            if node_xpath:
                return node_xpath, node_uid
            else:
                return next(self)
        else:
            return next(self)

    @staticmethod
    def xpath_parsing(node):
        """
        :param node: a node obj
        :return: xpath expression
        """
        invalid_res = (None, '')
        node_attrib = node.attrib
        class_name = node_attrib.get('class')
        resource_id = node_attrib.get('resource-id')
        text = node_attrib.get('text')
        content_desc = node_attrib.get('content-desc')

        # when text include \" will lead xpath error.
        if text not in invalid_res:
            if '"' in text:
                text = ''
        if class_name == 'hierarchy':
            return None
        elif content_desc not in invalid_res:
            return "*[@content-desc=\"%s\"]" % content_desc
        elif resource_id not in invalid_res and text not in invalid_res:
            return "*[@resource-id=\"%s\" and @text=\"%s\"]" % (resource_id, text)
        elif resource_id not in invalid_res:
            return "*[@resource-id=\"%s\"]" % resource_id
        elif text not in invalid_res:
            return "*[@text=\"%s\"]" % text
        else:
            return "*"

    # def generate_element_uid(self, node_attrib: dict):
    #     uid = ''
    #     invalid_list = {None, '', 'false'}
    #     # 'index'
    #     attrib_list = ['package', 'class', 'resource-id', 'content-desc',
    #                    'text', 'checkable', 'checked', 'clickable', 'enabled', 'focusable',
    #                    'long-clickable', 'password', 'scrollable', 'selected', 'displayed']
    #
    #     for attrib in attrib_list:
    #         value = node_attrib.get(attrib)
    #         if value not in invalid_list:
    #             uid += value
    #         uid = self.__page.current_activity + ':' + uid
    #     return uid


class ElementUid:

    def __init__(self, node_attrib: dict, activity=None):
        self.node_attrib = node_attrib
        self.__bounds = None
        self.__uid = ''
        invalid_list = {None, '', 'false'}
        # 'index'
        attrib_list = ['package', 'class', 'resource-id', 'content-desc',
                       'text', 'checkable', 'checked', 'clickable', 'enabled', 'focusable',
                       'long-clickable', 'password', 'scrollable', 'selected', 'displayed']

        for attrib in attrib_list:
            value = self.node_attrib.get(attrib)
            if value not in invalid_list:
                self.__uid += value
            self.__uid = activity + ':' + self.__uid

        position_str = self.node_attrib.get('bounds')
        if position_str:
            position_list = re.findall(r'\d+', position_str)
            self.__bounds = ((int(position_list[0]), int(position_list[1])),
                              (int(position_list[2]), int(position_list[3])))


    @property
    def uid(self):
        return self.__uid

    @property
    def bounds(self):
        return self.__bounds

    def __call__(self):
        return self.uid, self.bounds






