#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10

from page_parse import PageParse
from xpath_util import XpathParseIteration


class TestXpathUtil:

    @classmethod
    def setup_class(cls):
        page_xml = ''
        with open('testdata/pageSource/pageSource.xml', 'r', encoding='utf-8') as f:
            for line in f.readlines():
                page_xml += line
        page = PageParse(page_xml)
        cls.root = page.current_page_root

    def setup(self):
        self.seen = set()
        print('Test start.')

    def teardown(self):
        print('Test end.')

    def test_xpath_parse(self):
        xpath = XpathParseIteration(self.root, self.seen)
        assert len(list(xpath)) > 0

    def test_xpath_parse_skip_seen(self):
        xpath = XpathParseIteration(self.root, self.seen)
        # add all element to seen
        for i in xpath:
            if i[1] not in self.seen:
                self.seen.add(i[1])

        xpath2 = XpathParseIteration(self.root, self.seen)
        # pop last element
        self.seen.pop()
        count = 0
        # check same xml page, seen skip is work.
        for j in xpath2:
            count += 1
        assert count == 1


