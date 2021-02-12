#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/10

import pytest
from lxml.etree import XMLSyntaxError

from page_parse import PageParse


class TestPageParse:

    def setup(self):
        print("Test start.")

    def teardown(self):
        print("Test end.")

    def get_page_xml(self, path):
        page_xml = ''
        with open(path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                page_xml += line
        return page_xml

    def test_page_parse_init(self):
        page_xml = self.get_page_xml('testdata/pageSource/pageSource.xml')
        page = PageParse(page_xml)
        print(page)

    @pytest.mark.parametrize("path", ['testdata/pageSource/pageSource.xml'])
    def test_page_parse_equal(self, path):
        page_xml = self.get_page_xml(path)
        page1 = PageParse(page_xml)
        page2 = PageParse(page_xml)
        assert page1 == page2

    @pytest.mark.parametrize("path", ['testdata/pageSource/pageSource.xml'])
    def test_page_parse_equal_str(self, path):
        page_xml = self.get_page_xml(path)
        page1 = PageParse(page_xml)
        assert page1 == page_xml

    @pytest.mark.parametrize("path", [('testdata/pageSource/pageSource.xml',
                                       'testdata/pageSource/pageSource_2.xml')])
    def test_page_parse_not_equal(self, path):
        page_xml_1 = self.get_page_xml(path[0])
        page_xml_2 = self.get_page_xml(path[1])
        page1 = PageParse(page_xml_1)
        page2 = PageParse(page_xml_2)
        assert page1 != page2

    @pytest.mark.parametrize("path", [('testdata/pageSource/pageSource.xml',
                                       'testdata/pageSource/pageSource_2.xml')])
    def test_page_parse_not_equal_str(self, path):
        page_xml_1 = self.get_page_xml(path[0])
        page_xml_2 = self.get_page_xml(path[1])
        page1 = PageParse(page_xml_1)
        assert page1 != page_xml_2

    @pytest.mark.parametrize("path", ['testdata/pageSource/pageSource.xml'])
    def test_page_parse_equal_str_error(self, path):
        with pytest.raises(expected_exception=XMLSyntaxError):
            page_xml_1 = self.get_page_xml(path)
            page_xml_2 = "test"
            page1 = PageParse(page_xml_1)
            assert page1 != page_xml_2





