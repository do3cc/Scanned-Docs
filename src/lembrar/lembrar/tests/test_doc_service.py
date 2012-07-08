#!/usr/bin/python
# -*- coding: utf-8 -*-
import gridfs
import json
import pymongo
from lembrar.tests import config


#class test_service(object):
#
#    def setUp(self):
#        from lembrar import main
#        from webtest import TestApp
#        app = main({}, **{
#            'mongodb.url': config.get('test', 'mongodburl'),
#            'mongodb.db_name': 'test',
#            'mongodb.user': 'test',
#            'mongodb.passwd': 'test',
#            'accepted_languages': 'de,en',
#            'plugin.registry.host': '127.0.0.1',
#            'plugin.events.broker.in.port': '7001',
#            })
#        self.testapp = TestApp(app)
#        self.db = pymongo.Connection(config.get('test', 'mongodburl'
#                ))['test']
#        self.db.authenticate('test', 'test')
#
#    def tearDown(self):
#        self.db.docs.remove({})
#
#    def test_empty_add(self):
#        self.testapp.put('/doc', status=400)
#
#    def test_bad_date(self):
#        retval = self.testapp.put('/doc', dict(title='test',
#                                  created='tomorrow'), status=400,
#                                  upload_files=(('file', 'filename',
#                                  '123'), ))
#        assert [True for x in json.loads(retval.body)['errors']
#                if x['description'] == 'Cannot parse date format']
#
#    def test_add(self):
#        response = self.testapp.put('/doc', dict(title='Test'),
#                                    upload_files=(('file', 'filename',
#                                    '123'), ))
#        id = pymongo.objectid.ObjectId(json.loads(response.body)['id'])
#        new_doc = self.db.docs.find_one(dict(_id=id))
#        file_data = gridfs.GridFS(self.db).get(new_doc['raw_data'])
#        assert new_doc['version'] >= 5
#        assert '123' == file_data.read()
