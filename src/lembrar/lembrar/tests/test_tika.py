#!/usr/bin/python
# -*- coding: utf-8 -*-
from os import path
from pkg_resources import resource_stream, resource_filename
import datetime
from mock import Mock, call


class test_tika(object):

    def setUp(self):
        self.db = Mock()
        datastream = resource_stream(__name__, 'test.odt')
        self.db.find_one().raw_data = datastream.read()
        self.tikapath = path.sep.split(resource_filename(__name__, ''))
        self.tikapath = path.sep.join(self.tikapath[:-3]
                + ['tika-app.jar'])
        from lembrar.plugins import tika
        reload(tika)

    def test_async(self):
        from lembrar.plugins import tika
        tika.parser_task = Mock()
        tika.parser()
        assert [call.delay([], False)] == tika.parser_task.mock_calls

    def test_parser_task(self):
        from lembrar.plugins import tika
        tika.handle_update = Mock()
        tika.get_doc_db = Mock()
        tika.get_doc_db().find_unparsed.return_value = [1]
        tika.parser_task(tikapath='ignore', docids=[None], initial=True)
        assert [call(1, 'ignore', '0.1'), call(tika.get_doc_db(),
                'ignore', '0.1')] == tika.handle_update.mock_calls

    def test_tika(self):
        from lembrar.plugins import tika
        tika.handle_update(self.db, 'docid', self.tikapath, '1.0')
        is_ = self.db.find_one()
        assert [
            call.update_plugin_and_canonical_attr('content_type',
                    'application/vnd.oasis.opendocument.text'),
            call.update_plugin_and_canonical_attr('created',
                    datetime.datetime(
                2012,
                2,
                27,
                0,
                12,
                18,
                )),
            call.update_plugin_attr('full_html',
                                    '<p xmlns="http://www.w3.org/1999/xhtml">Hello World</p>\n'
                                    ),
            call.register_html_representation('full_html'),
            call.update_plugin('text', 'Hello World'),
            call.register_searchable_field('text'),
            call.update_plugin_and_canonical_attr('description',
                    'Hello World'),
            call.finish_parsing('1.0'),
            call.reindex(),
            ] == is_.mock_calls
