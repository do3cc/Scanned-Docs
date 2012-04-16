#!/usr/bin/python
# -*- coding: utf-8 -*-

from cornice import Service
from datetime import datetime
from gridfs import GridFS
from pymongo.objectid import ObjectId
from pyramid.url import route_url
from webob import Response
import json
import zmq

from scanned_docs.index import index
from scanned_docs.utils import convertStringToDateTime

doc_service = Service(name='doc', path='/doc*docid')


def exists(*args):

    def validator(request):
        for arg in args:
            if arg not in request.params:
                request.errors.add('parameters', arg, 'Is missing')
            else:
                request.validated[arg] = request.params[arg]

    return validator


def date_converter(request):
    created_string = request.params.get('created', '')
    if created_string:
        try:
            created = convertStringToDateTime(created_string)
        except:
            request.errors.add('parameters', 'crated',
                               'Cannot parse date format')
            return
    else:
        created = datetime.utcnow()
    request.validated['created'] = created


@doc_service.put(validator=(exists('title', 'file'), date_converter))
def add(request):
    title = request.params['title']
    created = request.validated['created'] or datetime.utcnow()

    description = request.params.get('description', '')

    datastream = request.params['file'].file

    doc_list = request.db.docs
    grid = GridFS(request.db)
    params = {}
    for key in request.params.keys():
        if key not in ['title', 'created', 'description', 'file']:
            params[key] = request.params[key]
    params.update(dict(title=title, description=description,
                  created=created, version=5,
                  raw_data=grid.put(datastream),
                  fulltext_fields=['description', 'title']))
    indexed_text = list(index(" ".join([title, description])))
    params['search_terms'] = indexed_text
    id = doc_list.insert(params)

    settings = request.registry.settings
    try:
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        socket.connect('tcp://%(plugin.registry.host)s:%(plugin.events.broker.in.port)s'
                        % settings)
        socket.setsockopt(zmq.LINGER, 100)
        socket.send('new ' + str(id), zmq.NOBLOCK)
        socket.close()
    except Exception, e:
        print e

    return dict(id=str(id))


@doc_service.get()
def get(request):
    if request.matchdict['docid']:
        return get_one(request)
    else:
        return get_many(request)


def get_one(request):
    id_ = request.matchdict['docid'][0]
    doc = request.db.docs.find_one({'_id': ObjectId(id_)})
    grid = GridFS(request.db)

    response = Response(grid.get(doc['raw_data']).read())
    if 'content_type' in doc:
        response.content_type = doc['content_type']
    return response


def get_many(request):
    query_args = {}
    if 'filter' in request.params and request.params['filter'].strip():
        keys = list(index(request.params['filter']))
        query_args.update({'search_terms': {'$in': keys}})
    if 'keyword' in request.params and request.params['keyword'].strip():
        query_args.update({'keywords': {'$in': [request.params['keyword'
                          ]]}})
    if 'id' in request.params and request.params['id'].strip():
        query_args = {'_id': ObjectId(request.params['id'])}
    if 'page' in request.params:
        page = int(request.params['page'])
    else:
        page = 0
    docs = request.db.docs.find(spec=query_args)
    totals = docs.count()
    docs = docs.skip(page * 10).limit(10)

    url_maker = lambda x: route_url(doc_service.route_name, request,
                                    docid=doc['_id'])

    def make_dict(result):
        retval = {}
        ignores = ['raw_data', '_id', 'fulltext_fields', 'created', 'search_terms', 'full_htmls']
        if 'full_htmls' in result:
            ignores += result['full_htmls']
        if 'fulltext_fields' in result:
            ignores += result['fulltext_fields']
        prefix_ignores = ['tika']
        for key in result.keys():
            ignore = False
            if key in ignores:
                continue
            for prefix in prefix_ignores:
                if key.startswith(prefix):
                    ignore = True
                    break
            if ignore:
                continue
            retval[key] = result[key]
        retval['resource_url'] = url_maker(result)
        retval['id'] = str(result['_id'])
        retval['created'] = result['created'].isoformat()
        retval['title'] = result['title']
        retval['description'] = result['description']
        return retval


    return dict(total=totals, results=[make_dict(doc) for doc in docs])


plugins_service = Service(name='plugins', path='/plugins')


@plugins_service.put()
def register(request):
    settings = request.registry.settings
    data = json.loads(request.body)
    print data
    assert data['version'] == 1
    return dict(couch_conn=settings['mongodb.url'],
                couch_db_name=settings['mongodb.db_name'],
                subscribe_conn='tcp://%(plugin.registry.host)s:%(plugin.events.broker.out.port)s'
                 % settings)
