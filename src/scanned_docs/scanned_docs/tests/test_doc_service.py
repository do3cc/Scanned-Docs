#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymongo
import gridfs
import json


class test_service(object):

    def setUp(self):
        from scanned_docs import main
        from webtest import TestApp
        app = main({}, **{'mongodb.url': 'localhost:10000',
                   'mongodb.db_name': 'test'})
        self.testapp = TestApp(app)
        self.db = pymongo.Connection('localhost:10000')['test']

    def test_empty_add(self):
        self.testapp.put('/doc', status=400)

    def test_bad_date(self):
        retval = self.testapp.put('/doc', dict(title='test',
                                  created='tomorrow'), status=400,
                                  upload_files=(('file', 'filename',
                                  '123'), ))
        assert [True for x in json.loads(retval.body)['errors'] if x['description'] == 'Cannot parse date format']

    def test_add(self):
        response = self.testapp.put('/doc', dict(title='Test'),
                                    upload_files=(('file', 'filename',
                                    '123'), ))
        id = pymongo.objectid.ObjectId(json.loads(response.body)['id'])
        new_doc = self.db.docs.find_one(dict(_id=id))
        file_data = gridfs.GridFS(self.db).get(new_doc['raw_data'])
        assert new_doc['version'] >= 5
        assert '123' == file_data.read()
