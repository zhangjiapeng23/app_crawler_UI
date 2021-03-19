#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10

from collections import deque

from lxml import etree

from xpath_util import XpathParseIteration

class PageParse:

    def __init__(self, page_source, page_activity=None):
        element_obj = etree.fromstring(page_source.encode('utf-8'))
        dom_obj = etree.ElementTree(element_obj)
        self.__current_page_root = dom_obj.getroot()
        self.__current_activity = page_activity

    @property
    def current_page_root(self):
        return self.__current_page_root

    @property
    def current_activity(self):
        return self.__current_activity

    def __eq__(self, other):
        if isinstance(other, PageParse):
            stack = deque()
            stack.append(self.current_page_root)
            stack.append(other.current_page_root)
            while stack:
                node1 = stack.pop()
                node2 = stack.pop()
                if node1.tag != node2.tag:
                    return False
                for node1, node2 in zip(node1, node2):
                    stack.append(node1)
                    stack.append(node2)
            return True
        elif isinstance(other, XpathParseIteration):
            return other == self
        else:
            return self == PageParse(other)

    def __repr__(self):
        return type(self).__name__ + '{}'.format(self.current_page_root)

    def __call__(self):
        return self.__current_page_root











