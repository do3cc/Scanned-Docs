#!/usr/bin/python
# -*- coding: utf-8 -*-
from mock import MagicMock, call


class test_service(object):

    def tearDown(self):
        from lembrar import service
        reload(service)

    def test_date_converter1(self):
        from lembrar.service import date_converter
        from datetime import datetime
        before = datetime.utcnow()
        request = MagicMock()
        request.validated = {}
        request.params = {}
        date_converter(request)
        after = datetime.utcnow()
        assert before <= request.validated['created'] <= after

    def test_date_converter2(self):
        from lembrar.service import date_converter
        request = MagicMock()
        request.validated = {}
        request.params = {}
        request.params['created'] = 'crap'
        date_converter(request)
        assert [call.add('parameters', 'created',
                'Cannot parse date format')] \
            == request.errors.mock_calls

    def test_date_converter3(self):
        from lembrar.service import date_converter
        from datetime import datetime
        request = MagicMock()
        request.validated = {}
        request.params = {}
        request.params['created'] = '2011-07-22 10:11:33'
        date_converter(request)
        assert datetime(
            2011,
            7,
            22,
            10,
            11,
            33,
            ) == request.validated['created']

    def test_collection_get1(self):
        from lembrar import service
        db = MagicMock()
        service.get_doc_db_from_request = lambda x: db
        request = MagicMock()
        request.params = {}
        test_ob = service.Docs(request)
        fake_doc = MagicMock()

        def find(limit, skip):
            return [fake_doc]

        db.find = find
        assert [fake_doc.to_jsonable_dict()] == test_ob.collection_get()

    def test_collection_get2(self):
        from lembrar import service
        db = MagicMock()
        service.get_doc_db_from_request = lambda x: db
        request = MagicMock()
        request.params = {}
        test_ob = service.Docs(request)
        request.params['skip'] = 20
        test_ob.collection_get()
        assert call(skip=20, limit=20) == db.find.mock_calls[0]

    def test_collection_put(self):
        from lembrar import service
        db = MagicMock()
        service.get_doc_db_from_request = lambda x: db
        request = MagicMock()
        request.params = dict(test='test1', file=MagicMock())
        test_ob = service.Docs(request)
        test_ob.collection_put()
        assert [call(request.params['file'].file,
                request.validated['created'], test='test1')] \
            == db.add_one.mock_calls
