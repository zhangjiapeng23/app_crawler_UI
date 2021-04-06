#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10
import re
import uuid
from collections import deque, namedtuple

from log  import log


class XpathParseIteration:
    node_obj = namedtuple('node_obj', ['node', 'node_uid'])

    def __init__(self, page, first_elements_config, last_elements_config):
        LAST_ELEMENTS = last_elements_config
        FIRST_ELEMENTS = first_elements_config
        # record last click elements.
        self.last = []
        self.page = page
        # page_root: curent page xml root node.
        self.root = page.current_page_root
        # record each node parent: {cur_node: par_node}
        self.__routing = {}
        # record each node xpath string. {node: 'xxxx'}
        self.__xpath_mapping = {}
        # each node will be key of routing map, add attr uuid to keep unique.
        self.root.set('uuid', str(uuid.uuid1()))
        # root not have parent node
        self.__routing[self.root] = None
        # create a post order list
        self.__postorder = deque()
        stack = deque()
        # push root node to stack.
        node_uid = ElementUid(node_attrib=self.root.attrib, activity=self.page.current_activity)
        node = self.node_obj(self.root, node_uid)
        stack.append(node)
        last_elements = []
        first_elements = []
        while stack:
            node = stack.pop()

            if self.__re_search(node.node_uid.uid, FIRST_ELEMENTS):
                # log.debug(f"find first element {node.node_uid.uid}")
                first_elements.append(node)
            elif self.__re_search(node.node_uid.uid, LAST_ELEMENTS):
                # log.debug(f"find last element {node.node_uid.uid}")
                last_elements.append(node)

            else:
                self.__postorder.append(node)
                for child in node.node:
                    child.set('uuid', str(uuid.uuid1()))
                    self.__routing[child] = node.node
                    node_uid = ElementUid(node_attrib=child.attrib, activity=self.page.current_activity)
                    child_obj = self.node_obj(child, node_uid)
                    stack.append(child_obj)
        else:
            self.__postorder.extendleft(last_elements)
            self.__postorder.extend(first_elements)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            node = self.__postorder.pop()
        except IndexError as exc:
            raise StopIteration(exc)
        else:
            return self.xpath(node)

    def xpath(self, node):
        node_xpath_fmt = '//{}//{}'
        v_node, node_uid = node.node, node.node_uid
        k_node = self.__routing[v_node]
        if v_node is not None and k_node is not None:
            if k_node not in self.__xpath_mapping.keys():
                k_xpath = self.xpath_parsing(k_node)
                self.__xpath_mapping[k_node] = k_xpath
            else:
                k_xpath = self.__xpath_mapping[k_node]
            v_xpath = self.xpath_parsing(v_node)
            node_xpath = node_xpath_fmt.format(k_xpath, v_xpath)
            return node_xpath, node_uid
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

    def __eq__(self, other):
        return self.page == other

    @staticmethod
    def __re_search(target, _list):
        for item in _list:
            if re.search(r'{}'.format(item), target):
                return True
        return False


class ElementUid:

    def __init__(self, node_attrib: dict, activity=None):
        self.node_attrib = node_attrib
        self.__bounds = None
        self.__uid = ''
        invalid_list = {None, '', 'false'}
        # 'index', 'package'
        attrib_list = ['checkable', 'checked', 'clickable', 'enabled', 'focusable',
                       'long-clickable', 'password', 'scrollable', 'selected', 'displayed',
                       'class', 'text', 'content-desc', 'resource-id']

        for attrib in attrib_list:
            value = self.node_attrib.get(attrib)
            if value not in invalid_list:
                if value == 'true':
                    self.__uid += '1'
                else:
                    self.__uid += value
        self.__uid = activity + ':' + self.__uid

        position_str = self.node_attrib.get('bounds')
        if position_str:
            position_list = re.findall(r'\d+', position_str)
            self.__bounds = ((int(position_list[0]), int(position_list[1])),
                              (int(position_list[2]), int(position_list[3])))


    @property
    def uid(self):
        # format is “activity:classxxxxtest010....”
        # include current activity and node each attributes info.
        return self.__uid

    @property
    def bounds(self):
        return self.__bounds

    def __call__(self):
        return self.uid, self.bounds






