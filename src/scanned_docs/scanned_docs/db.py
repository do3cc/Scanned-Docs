#!/usr/bin/python
# -*- coding: utf-8 -*-
from pymongo.objectid import ObjectId
import pymongo
from scanned_docs.index import index
import gridfs
import os


class Doc(object):

    '''Represents a single document.'''

    def __init__(
        self,
        doc,
        db,
        grid,
        accepted_languages,
        prefix,
        ):

        self.db = db
        self.doc = doc
        self.accepted_languages = accepted_languages
        self.prefix = prefix
        self.raw_data_file = grid.get(doc['raw_data'])

    @property
    def raw_data(self):
        '''
        Return the raw data of the uploaded document.
        '''

        return self.raw_data_file.read()

    def update_plugin_attr(self, key, value):
        '''
        Update a document property.
        To avoid naming collisions with other plugins,
        a prefix is required.

        :param key: The property name
        :type key: string
        :param value: The property value
        :type value: string
        '''

        self.doc[self.prefixed_name(key)] = value
        self.db.save(self.doc)

    def update_plugin_and_canonical_attr(self, key, value):
        '''
        Update a document property, and the update_plugin_and_canonical
        version without a prefix.
        Only update the canonical value if no value has
        been set yet.
        Example: content_type
        To avoid naming collisions with other plugins,
        a prefix is required.

        :param key: The property name
        :type key: string
        :param value: The property value
        :type value: string
        '''

        self.update(key, value)
        if key not in self.doc:
            self.doc[key] = value
        self.db.save(self.doc)

    def register_html_representation(self, field):
        '''
        Register a html representation.
        as one of the fields that contain a html representation.

        :param field: The fieldname that contains html
        :type field: string
        '''

        fieldname = self.prefixed_name(field)
        if not 'full_htmls' in self.doc:
            self.doc['full_htmls'] = []
        if fieldname not in self.doc['full_htmls']:
            self.doc['full_htmls'].append(fieldname)
        self.db.save(self.doc)

    def register_searchable_field(self, field):
        '''
        Register a field that must be considered for full text search

        :param field: The fieldname that contains text to search for
        :type field: string
        '''

        fieldname = self.prefixed_name(field)
        if not 'searchable_fields' in self.doc:
            self.doc['searchable_fields'] = []
        if fieldname not in self.doc['searchable_fields']:
            self.doc['searchable_fields'].append(fieldname)
        self.db.save(self.doc)

    def prefixed_name(self, field):
        return self.prefix + '_' + field

    def reindex(self):
        '''
        Reindex the document
        '''

        text_to_index = []
        for field in self.doc['fulltext_fields']:
            text_to_index.append(self.doc[field])
        indexed_text = list(index(' '.join(text_to_index),
                            accepted_languages=self.accepted_languages))
        self.doc['search_terms'] = indexed_text
        self.db.save(self.doc)

    def finish_parsing(self, version):
        '''
        Store a property on the document that helps to find objects not yet
        indexed
        :param version: A version identifier
        :type version: string
        '''

        self.update_plugin_attr('version', version)


class DocDB(object):

    '''
    Thin wrapper of mongodb. Returns wrapped results with
    :py:class:`lembrar.db.Doc`.
    Use :py:func:`lembrar.db.get_doc_db` to get an instance of this class.
    '''

    def __init__(
        self,
        db,
        grid,
        accepted_languages,
        prefix,
        ):

        self.db = db
        self.grid = grid
        self.accepted_languages = accepted_languages
        self.prefix = prefix

    def find(self, *args, **kw):
        '''
        Find like in mongodb. If you filter the returned fields,
        bad things might happen
        '''

        for doc in self.db.docs.find(*args, **kw):
            yield Doc(doc, self.db, self.grid, self.accepted_languages,
                      self.prefix)

    def find_one(self, id):
        '''Find one like in mongodb'''

        id = ObjectId(id)
        return Doc(self.db.docs.find_one(dict(_id=id)), self.db,
                   self.grid, self.accepted_languages, self.prefix)

    def find_unparsed(self, version):
        '''
        Find all documents that have not been parsed yet
        :param version: Version identifier
        :type version: string
        '''

        return self.find(dict(version=version))


def get_doc_db(
    prefix='',
    db_dsn=None,
    db_name=None,
    grid=None,
    accepted_languages=None,
    ):
    '''
    Create a :py:class:`lembrar.db.DocDB` instance.

    :param prefix: The prefix is a string that is used to avoid name clashes
        When different plugins want to set the same attributes on a document
    :type prefix: string
    '''

    db_dsn = db_dsn or os.environ.get('mongodb_dsn')
    db_name = db_name or os.environ.get('mongodb_db')
    accepted_languages = accepted_languages \
        or os.environ.get('accepted_languages').split(',')
    conn = pymongo.Connection(db_dsn)
    db = conn[db_name]
    grid = grid or gridfs.GridFS(db)
    docdb = DocDB(db, grid, accepted_languages, prefix)
    return docdb
