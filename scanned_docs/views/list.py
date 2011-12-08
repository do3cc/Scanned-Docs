from pymongo import DESCENDING
from pymongo.objectid import ObjectId
from pyramid.httpexceptions import HTTPFound
from scanned_docs.index import index
from webhelpers.paginate import Page, PageURL_WebOb
import mimetypes
import os

from webob import Response


def list_view(request):
    query_args = {}
    if 'filter' in request.params:
        keys = list(index(request.params['filter']))
        query_args.update({'search_terms': {'$in': keys}})
    if 'keyword' in request.params:
        query_args.update({'keywords': {'$in': [request.params['keyword']]}})
    docs = request.db.docs.find(spec=query_args)
    docs.sort('created', DESCENDING)
    item_count = docs.count()

    page = int(request.params.get('page', 1))
    items_per_page = 10

    url_maker = PageURL_WebOb(request)
    docs = Page(list(docs[(page - 1) * items_per_page:page * items_per_page]),
                url=url_maker,
                page=page,
                items_per_page=items_per_page,
                item_count=item_count,
                presliced_list=True)

    distinct_keywords = request.db.docs.distinct('keywords')
    distinct_keywords.sort()
    return {'docs': docs,
            'distinct_keywords': distinct_keywords}


def image(request):
    bla = request.db.docs.find({'_id': ObjectId(request.matchdict['id'])})[0]

    response = Response(bla['img'])
    #mt, encoding = mimetypes.guess_type(filename)
    response.content_type = 'image/jpeg'
    return response


def thumb(request):
    bla = request.db.docs.find({'_id': ObjectId(request.matchdict['id'])})[0]

    response = Response(bla['thumb'])
    #mt, encoding = mimetypes.guess_type(filename)
    response.content_type = 'image/jpeg'
    return response


def delete(request):
    bla = request.db.docs.find({'_id': ObjectId(request.matchdict['id'])})[0]
    request.db.docs.remove(bla)
    url = request.resource_url(request.context)
    return HTTPFound(location=url)
