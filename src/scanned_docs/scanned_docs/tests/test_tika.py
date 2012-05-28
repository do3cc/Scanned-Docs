#!/usr/bin/python
# -*- coding: utf-8 -*-
from os import path
from pkg_resources import resource_stream, resource_filename
from pyramid.threadlocal import get_current_registry
import datetime
import gridfs
import pymongo

from scanned_docs.tests import config


class test_tika(object):

    def setUp(self):
        self.db = pymongo.Connection(config.get('test', 'mongodburl'
                ))['test']
        grid = gridfs.GridFS(self.db)
        datastream = resource_stream(__name__, 'test.odt')
        self.new_doc = self.db.docs.insert(dict(title='test',
                description='description', version=5,
                raw_data=grid.put(datastream)))
        self.tikapath = path.sep.split(resource_filename(__name__, ''))

        # XXX Get rid of explicit tika version mentions

        self.tikapath = path.sep.join(self.tikapath[:-3]
                + ['tika-app-1.0.jar'])

        # XXX must find a way to avoid this

        registry = get_current_registry()
        if not registry.settings:
            registry.settings = {}
        registry.settings['accepted_languages'] = 'de,en'

    def test_tika(self):
        from scanned_docs.plugins import tika

        class Args(object):

            tikapath = self.tikapath
            accepted_languages = 'de,en'

        tika.handle_update(self.db, Args, str(self.new_doc))
        should_be = {
            u'fulltext_fields': [u'tika_text'],
            u'tika_content_type': u'application/vnd.oasis.opendocument'\
                u'.text',
            u'description': u'description',
            u'created': datetime.datetime(
                2012,
                2,
                27,
                0,
                12,
                18,
                ),
            u'tika_description': u'Hello World',
            u'title': u'test',
            u'search_terms': [u'World', u'hello'],
            u'tika_version': 1,
            u'version': 5,
            u'tika_created': datetime.datetime(
                2012,
                2,
                27,
                0,
                12,
                18,
                ),
            u'content_type': u'application/vnd.oasis.opendocument.text',
            u'tika_full_html': u'<p xmlns="http://www.w3.org/1999/xhtm'\
                u'l">Hello World</p>\n',
            u'full_htmls': [u'tika_full_html'],
            u'tika_text': u'Hello World',
            }
        is_ = self.db.docs.find_one({'_id': self.new_doc})
        is_.pop('_id')
        is_.pop('raw_data')
        assert should_be == is_
