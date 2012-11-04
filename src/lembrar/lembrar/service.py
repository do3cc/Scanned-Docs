#!/usr/bin/python
# -*- coding: utf-8 -*-

from cornice import Service, resource
from datetime import datetime
from gridfs import GridFS
from pymongo.objectid import ObjectId
from pyramid.url import route_url
from webob import Response
import json
import math

from lembrar.db import get_doc_db_from_request
from lembrar.index import index
from lembrar.utils import convertStringToDateTime
from lembrar.image import get_thumbnail


def date_converter(request):
    created_string = request.params.get('created', '')
    if created_string:
        try:
            created = convertStringToDateTime(created_string)
        except:
            request.errors.add('parameters', 'created',
                               'Cannot parse date format')
            return
    else:
        created = datetime.utcnow()
    request.validated['created'] = created


def int_converter(keys):
    def validator(request):
        for key in keys:
            if key in request.params:
                request.validated[key] = int(request.params[key])
    return validator


binary = Service(name='binary', path='/binary_doc/{docid}', description="Binary doc data")

stats = Service(name='stats', path="/stats/{statname}", description="Statistics")

@stats.get()
def get_stats(request):
    statname = request.matchdict['statname']
    db = get_doc_db_from_request(request)
    return db.get_stat(statname)

@binary.get()
def get_binary(request):
    """Returns Hello in JSON."""
    id_ = request.matchdict['docid']
    db = get_doc_db_from_request(request)
    doc = db.find_one(id_)
    data = doc.raw_data
    response = Response(data)
    if 'content_type' in doc:
        response.content_type = doc.get('content_type')
    return response

preview = Service(name='preview', path="/preview_doc/{docid}")

@preview.get()
def get_preview(request):
    id_ = request.matchdict['docid']
    db = get_doc_db_from_request(request)
    doc = db.find_one(id_)
    data = doc.raw_data
    if 'content_type' in doc:
        content_type = doc.get('content_type')
    else:
        content_type = 'text/html'
    if content_type.startswith('image'):
        data = get_thumbnail(data)
    response = Response(data)
    response.content_type = content_type

    return response


htmls = Service(name="htmls", path="/htmls_doc/{docid}")

@htmls.get()
def get_htmls(request):
    """Returns Hello in JSON."""
    id_ = request.matchdict['docid']
    db = get_doc_db_from_request(request)
    doc = db.find_one(id_)
    return doc.get_html_representations()

@resource.resource(collection_path='/docs', path='/docs/{id}')
class Docs(object):

    def __init__(self, request):
        self.request = request
        self.db = get_doc_db_from_request(request)

    @resource.view(renderer='json', validators=(int_converter(['page']), ))
    def collection_get(self):
        
        limit = 2
        page = self.request.validated.get('page', 0)


        if "filter" in self.request.params:
            keys = list(index(self.request.params["filter"]))
            spec = {"search_terms": {"$in": keys}}
        else:
            spec = {}
        if page < 0:
            pages = int(self.db.count(spec) / limit)
            page = pages +1 +page
        return [x.to_jsonable_dict() for x in self.db.find(spec, limit=limit, 
            skip=page * limit, sort=[('created', 1)])]

    @resource.view(renderer='json')
    def get(self):
        import pdb;pdb.set_trace()

    @resource.view(renderer='json')
    def delete(self):
        result = self.db.remove_one(self.request.matchdict['id'])
        return result['err'] == None

    @resource.view(renderer='json', validators=(date_converter,))
    def put(self):
        docid = self.request.matchdict['id']
        docdata = json.loads(self.request.body)
        for key in ['created']:
            if key in docdata:
                docdata[key] = convertStringToDateTime(docdata[key])
        doc = self.db.find_one(docid)
        doc.update_from_dict(docdata)
        return 1

    @resource.view(renderer='json', validators=(date_converter,))
    def collection_put(self):
        file_reader = self.request.params['file'].file
        created = self.request.validated['created'] or datetime.utcnow()
        args = {}
        for key, value in self.request.params.items():
            if key not in ['created', 'file']:
                args[key] = value
        self.db.add_one(file_reader, created, **args)

# #@doc_service.get()
# def get(request):
#     if request.matchdict['docid']:
#         return get_one(request)
#     else:
#         return get_many(request)


# def get_one(request):
#     id_ = request.matchdict['docid'][0]
#     doc = request.db.docs.find_one({'_id': ObjectId(id_)})
#     grid = GridFS(request.db)

#     response = Response(grid.get(doc['raw_data']).read())
#     if 'content_type' in doc:
#         response.content_type = doc['content_type']
#     return response


# def get_many(request):
#     query_args = {}
#     if 'filter' in request.params and request.params['filter'].strip():
#         keys = list(index(request.params['filter']))
#         query_args.update({'search_terms': {'$in': keys}})
#     if 'keyword' in request.params and request.params['keyword'].strip():
#         query_args.update({'keywords': {'$in': [request.params['keyword'
#                           ]]}})
#     if 'id' in request.params and request.params['id'].strip():
#         query_args = {'_id': ObjectId(request.params['id'])}
#     if 'page' in request.params:
#         page = int(request.params['page'])
#     else:
#         page = 0
#     docs = request.db.docs.find(spec=query_args)
#     totals = docs.count()
#     docs = docs.skip(page * 10).limit(10)

#     url_maker = lambda x: route_url(doc_service.route_name, request,
#                                     docid=doc['_id'])

#     def make_dict(result):
#         retval = {}
#         ignores = ['raw_data', '_id', 'fulltext_fields', 'created', 'search_terms', 'full_htmls']
#         if 'full_htmls' in result:
#             ignores += result['full_htmls']
#         if 'fulltext_fields' in result:
#             ignores += result['fulltext_fields']
#         prefix_ignores = ['tika']
#         for key in result.keys():
#             ignore = False
#             if key in ignores:
#                 continue
#             for prefix in prefix_ignores:
#                 if key.startswith(prefix):
#                     ignore = True
#                     break
#             if ignore:
#                 continue
#             retval[key] = result[key]
#         retval['resource_url'] = url_maker(result)
#         retval['id'] = str(result['_id'])
#         retval['created'] = result['created'].isoformat()
#         retval['title'] = result['title']
#         retval['description'] = result['description']
#         return retval


#     return dict(total=totals, results=[make_dict(doc) for doc in docs])


# plugins_service = Service(name='plugins', path='/plugins')


# @plugins_service.put()
# def register(request):
#     settings = request.registry.settings
#     data = json.loads(request.body)
#     print data
#     assert data['version'] == 1
#     return dict(couch_conn=settings['mongodb.url'],
#                 couch_db_name=settings['mongodb.db_name'],
#                 subscribe_conn='tcp://%(plugin.registry.host)s:%(plugin.events.broker.out.port)s'
#                  % settings)
