#!/usr/bin/python
# -*- coding: utf-8 -*-
from mock import MagicMock, call


class test_doc_(object):

    def setUp(self):
        from lembrar import db
        from datetime import datetime
        reload(db)
        self.grid = MagicMock()
        self.created = datetime.now()
        self.doc = db.Doc(doc=dict(raw_data='raw_data', _id='123',
                          test='test1', created=self.created),
                          db=MagicMock(), grid=self.grid,
                          accepted_languages=MagicMock(),
                          prefix='prefix')

    def test_doc_get_raw_data(self):
        assert self.grid.get().read() == self.doc.raw_data

    def test_doc_to_jsonable_dict(self):
        assert dict(id='123', created=self.created.isoformat(),
                    test='test1') == self.doc.to_jsonable_dict()

    def test_doc_update_plugin_attr(self):
        self.doc.update_plugin_attr('key', 'value')
        assert 'value' == self.doc.doc['prefix_key']

    def test_doc_update_plugin_and_canonical_attr(self):
        self.doc.update_plugin_and_canonical_attr('key', 'value')
        assert 'value' == self.doc.doc['key']
        assert 'value' == self.doc.doc['prefix_key']

    def test_doc_register_html_representation(self):
        self.doc.register_html_representation('html_field_key')
        assert ['prefix_html_field_key'] == self.doc.doc['full_htmls']

    def test_doc_register_searchable_field(self):
        self.doc.register_searchable_field('search_field_key')
        assert ['prefix_search_field_key'] \
            == self.doc.doc['searchable_fields']

    def test_prefixed_name(self):
        assert 'prefix_test' == self.doc.prefixed_name('test')

    def test_reindex(self):
        from lembrar import db
        self.doc.doc['fulltext_fields'] = ['field1', 'field2']
        self.doc.doc['field1'] = 'text1'
        self.doc.doc['field2'] = 'text2'
        db.index = MagicMock()
        db.index.return_value = ['index', 'data']
        self.doc.reindex()
        assert call('text1 text2',
                    accepted_languages=self.doc.accepted_languages) \
            == db.index.mock_calls[0]
        assert ['index', 'data'] == self.doc.doc['search_terms']

    def test_finish_parsing(self):
        self.doc.finish_parsing('2.2')
        assert '2.2' == self.doc.doc['prefix_version']


class test_db(object):

    def setUp(self):
        from lembrar import db
        reload(db)
        self.db = db.DocDB(db=MagicMock(), grid=MagicMock(),
                           accepted_languages=MagicMock(),
                           prefix=MagicMock())
        db.notify_new_document = lambda x: x

    def tearDown(self):
        from lembrar import db
        reload(db)

    def test_find(self):
        doc = MagicMock()
        self.db.db.docs.find.return_value = [doc]
        results = [x for x in self.db.find(test=1)]
        assert call.find(test=1) == self.db.db.docs.mock_calls[0]
        assert 1 == len(results)
        assert doc == results[0].doc

    def test_find_one(self):
        from pymongo.objectid import ObjectId
        doc = MagicMock()
        self.db.db.docs.find_one.return_value = doc
        result = self.db.find_one('1' * 24)
        assert call.find_one({'_id': ObjectId('111111111111111111111111'
                             )}) == self.db.db.docs.mock_calls[0]
        assert doc == result.doc

    def test_add_one(self):
        from StringIO import StringIO
        from datetime import datetime
        now = datetime.utcnow()
        file_reader = StringIO('123')
        objid = self.db.add_one(file_reader, now, test=1)
        assert [call.put(file_reader)] == self.db.grid.mock_calls
        assert [call.insert({'test': 1, 'raw_data': self.db.grid.put(),
                'created': now})] == self.db.db.docs.mock_calls
        assert self.db.db.docs.insert() == objid

    def test_find_unparsed(self):
        doc = MagicMock()
        self.db.db.docs.find.return_value = [doc]
        results = [x for x in self.db.find_unparsed('1')]
        assert call.find({'version': '1'}) \
            == self.db.db.docs.mock_calls[0]
        assert 1 == len(results)
        assert doc == results[0].doc


class test_db_getter(object):

    def setUp(self):
        from lembrar import db
        reload(db)

    def test_db_getter(self):
        from lembrar import db
        db.pymongo = MagicMock()
        grid = MagicMock()
        new_db = db.get_doc_db('prefix', 'ds', 'db_name', grid, 'a,b')
        assert db.pymongo.Connection()[None] == new_db.db
        assert grid == new_db.grid
        assert 'a,b' == new_db.accepted_languages
        assert 'prefix' == new_db.prefix

    def test_db_getter_from_request(self):
        from lembrar import db
        db.gridfs = MagicMock()
        request = MagicMock()
        request.registry.settings = {}
        request.registry.settings['accepted_languages'] = 'a,b'
        new_db = db.get_doc_db_from_request(request)
        assert ['a', 'b'] == new_db.accepted_languages
        assert '' == new_db.prefix
        assert request.db == new_db.db
