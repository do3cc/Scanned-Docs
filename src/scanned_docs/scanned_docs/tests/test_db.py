#!/usr/bin/python
# -*- coding: utf-8 -*-
from mock import Mock


def test_docdb_passes_everything():
    from scanned_docs.db import DocDB

    db = Mock()
    docdb = DocDB(db, None, [], '')
    docs = list(docdb.find())
    doc = docs[0]
    assert len(docs) == 1
    assert doc.db == docdb.db
    assert doc.grid == docdb.grid
    assert doc.accepted_languages == docdb.accepted_languages == []


def test_docdb_find_one_converts_id():
    from scanned_docs.db import DocDB
    args = None

    class DB(object):

        def find_one(self, some_dict):
            args = some_dict
            return None

    docdb = DocDB(DB(), [], object())
    docdb.find_one('111')
    assert args['_id'] != '111'
