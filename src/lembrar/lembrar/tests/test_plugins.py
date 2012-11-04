#!/usr/bin/python
# -*- coding: utf-8 -*-
from mock import MagicMock, call


class test_plugins(object):

    def tearDown(self):
        from lembrar import plugins
        reload(plugins)

    def test_notify_new_document(self):
        from lembrar import plugins
        entry_point = MagicMock()

        def fake_entry_points(group):
            return [entry_point]

        plugins.iter_entry_points = fake_entry_points
        plugins.notify_new_document('docid')
        assert [call.load(), call.load()(initial=False, docids=['docid'
                ])] == entry_point.mock_calls
