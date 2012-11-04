#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from pymongo.objectid import ObjectId
from pyramid.threadlocal import get_current_registry
import gridfs
import os
import pymongo
from lembrar.index import index
from lembrar.plugins import notify_new_document


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

    def to_jsonable_dict(self):
        '''
        Return a dict of the document that can be converted to json,
        without any binary data.
        '''

        retval = {}
        for (key, value) in self.doc.items():
            if key not in ('raw_data', '_id'):
                if isinstance(value, datetime):
                    retval[key] = value.isoformat()
                else:
                    retval[key] = value
        retval['id'] = str(self.doc['_id'])
        return retval

    def update_from_dict(self, dict_):
        '''
        Update the data with something received from a dict
        '''
        for key, value in dict_.items():
            self.doc[key] = value
        self.reindex()

    @property
    def raw_data(self):
        '''
        Return the raw data of the uploaded document.
        '''

        return self.raw_data_file.read()

    def get(self, key):
        """
        Return the data of given key

        :param key: The property name
        :type key: string
        """
        return self.doc[key]

    def __contains__(self, key):
        """
        Return whether the document has a given key

        :param key: The property name
        :type key: string
        """
        return key in self.doc

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
        self.db.docs.save(self.doc)

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

        self.update_plugin_attr(key, value)
        if key not in self.doc:
            self.doc[key] = value
        self.db.docs.save(self.doc)

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
        self.db.docs.save(self.doc)

    def get_html_representations(self):
        """
        Return all registered html representations of the document
        """
        return [self.doc[x] for x in self.doc.get('full_htmls', [])]

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
        self.db.docs.save(self.doc)

    def prefixed_name(self, field):
        return self.prefix + '_' + field

    def reindex(self):
        '''
        Reindex the document
        '''

        text_to_index = [self.doc['title']]
        for field in self.doc.get('fulltext_fields', []):
            text_to_index.append(self.doc[field])
        indexed_text = list(index(' '.join(text_to_index),
                            accepted_languages=self.accepted_languages))
        self.doc['search_terms'] = indexed_text
        self.db.docs.save(self.doc)

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

    def count(self, *args, **kw):
        return self.db.docs.find(*args, **kw).count()


    def find_one(self, id):
        '''Find one like in mongodb'''

        id = ObjectId(id)
        return Doc(self.db.docs.find_one(dict(_id=id)), self.db,
                   self.grid, self.accepted_languages, self.prefix)

    def remove_one(self, id):
        """Remove one document with the given id
        :param id: The document id
        :type id: string
        """
        return self.db.docs.remove(ObjectId(id), safe=True)

    def add_one(
        self,
        file_reader,
        created,
        **kw
        ):
        '''Add one document, store all kwargs on it
        :param file_reader: The file data
        :type file_reader: An object that can be read from
        :param created: The time, the object got created
        :type created: datetime object without tz info and utc time
        '''

        params = dict(created=created,
                      raw_data=self.grid.put(file_reader))
        for (key, value) in kw.items():
            params[key] = value
        docid = self.db.docs.insert(params)
        notify_new_document(docid)
        return docid

    def find_unparsed(self, version):
        '''
        Find all documents that have not been parsed yet
        :param version: Version identifier
        :type version: string
        '''

        return self.find(dict(version=version))

    def get_stat(self, statname):
        '''
        '''
        if statname == 'tags':
            return self.db.docs.distinct('tags')
        else:
            return "undefined"


def get_doc_db(
    prefix='',
    db_dsn=None,
    db_name=None,
    grid=None,
    accepted_languages=None,
    user=None,
    password=None,
    ):
    '''
    Create a :py:class:`lembrar.db.DocDB` instance.

    :param prefix: The prefix is a string that is used to avoid name clashes
        When different plugins want to set the same attributes on a document
    :type prefix: string
    '''

    settings = get_current_registry().settings
    db_dsn = db_dsn or os.environ.get('mongodb_dsn') \
        or settings.get('mongodb_dsn')
    db_name = db_name or os.environ.get('mongodb_db') \
        or settings.get('mongodb_db')
    accepted_languages = accepted_languages \
        or (os.environ.get('accepted_languages')
            or settings.get('accepted_languages')).split(',')
    user = user or os.environ.get("mongodb_user") or settings.get("mongodb_user")
    password = password or os.environ.get("mongodb_password") or settings.get("mongodb_password")
    conn = pymongo.Connection(db_dsn)
    db = conn[db_name]
    db.authenticate(user, password)
    grid = grid or gridfs.GridFS(db)
    docdb = DocDB(db, grid, accepted_languages, prefix)
    return docdb


def get_doc_db_from_request(request):
    '''
    Create a :py:class:`lembrar.db.DocDB` instance from information of a
    request.

    :param request: The request from which we try to extract a DocDB
    :type request: a webob request object
    '''

    settings = request.registry.settings
    db = request.db
    grid = gridfs.GridFS(db)
    accepted_languages = (os.environ.get('accepted_languages')
                          or settings.get('accepted_languages'
                          )).split(',')
    prefix = ''
    docdb = DocDB(db, grid, accepted_languages, prefix)
    return docdb
