#!/usr/bin/python
# -*- coding: utf-8 -*-
from scanned_docs.tests import config


class test_views(object):

    def setUp(self):
        from scanned_docs import main
        from webtest import TestApp
        app = main({}, **{'mongodb.url': config.get('test', 'mongodburl'
                   ), 'mongodb.db_name': 'test',
               'mongodb.user': 'test',
                'mongodb.passwd': 'test'})
        self.testapp = TestApp(app)

    def test_home(self):
        assert self.testapp.get('/').status == '200 OK'
