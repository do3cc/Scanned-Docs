#!/usr/bin/python
# -*- coding: utf-8 -*-
from pymongo.objectid import ObjectId
import gridfs
from scanned_docs.index import index


class Doc(object):

    def __init__(
        self,
        doc,
        db,
        grid,
        accepted_languages
        ):

        self.db = db
        self.doc = doc
        self.accepted_languages = accepted_languages
        self.raw_data_file = grid.get(doc['raw_data'])

    @property
    def raw_data(self):
        return self.raw_data_file.read()

    def update_plugin(
        self,
        key,
        value,
        prefix,
        ):

        self.doc[self.prefixed_name(key, prefix)] = value
        self.db.save(self.doc)

    def update_plugin_and_canonical(
        self,
        key,
        value,
        prefix,
        ):

        self.update(key, value, prefix)
        fieldname = self.prefixed_name(key, prefix)
        if fieldname not in self.doc:
            self.doc[fieldname] = value
        self.db.save(self.doc)

    def register_html_representation(self, field, prefix):
        fieldname = self.prefixed_name(field, prefix)
        if not 'full_htmls' in self.doc:
            self.doc['full_htmls'] = []
        if fieldname not in self.doc['full_htmls']:
            self.doc['full_htmls'].append(fieldname)
        self.db.save(self.doc)

    def register_searchable_field(self, field, prefix):
        fieldname = self.prefixed_name(field, prefix)
        if not 'searchable_fields' in self.doc:
            self.doc['searchable_fields'] = []
        if fieldname not in self.doc['searchable_fields']:
            self.doc['searchable_fields'].append(fieldname)
        self.db.save(self.doc)

    def prefixed_name(self, field, prefix):
        return prefix + '_' + field

    def reindex(self):
        text_to_index = []
        for field in self.doc['fulltext_fields']:
            text_to_index.append(self.doc[field])
        indexed_text = list(index(' '.join(text_to_index),
                            accepted_languages=self.accepted_languages))
        self.doc['search_terms'] = indexed_text
        self.db.save(self.doc)


class DocDB(object):

    def __init__(self, db, accepted_languages):
        self.db = db
        self.grid = gridfs.GridFS(db)
        self.accepted_languages = accepted_languages

    def find(self, *args, **kw):
        for doc in self.db.docs.find(*args, **kw):
            yield Doc(doc, self.db, self.grid, self.accepted_languages)

    def find_one(self, id):
        id = ObjectId(id)
        return Doc(self.db.docs.find_one(dict(_id=id)), self.db,
                   self.grid, self.accepted_languages)
