# -*- coding: utf-8 -*-

from cornice import Service
from datetime import datetime
from gridfs import GridFS
from pymongo.objectid import ObjectId
from webob import Response
import json
import zmq

from scanned_docs.utils import convertStringToDateTime

doc_service = Service(name="doc", path="/doc*docid")


def exists(*args):

    def validator(request):
        for arg in args:
            if arg not in request.params:
                request.errors.add("parameters", arg, "Is missing")
            else:
                request.validated[arg] = request.params[arg]

    return validator


def date_converter(request):
    created_string = request.params.get("created", "")
    if created_string:
        try:
            created = convertStringToDateTime(created_string)
        except:
            request.errors.add("parameters", "crated",
                               "Cannot parse date format")
            return
    else:
        created = datetime.utcnow()
    request.validated["created"] = created


@doc_service.put(validator=(exists("title", "file"), date_converter))
def add(request):
    title = request.params["title"]
    created = request.params.get("created", datetime.utcnow()) \
        or datetime.utcnow()
    description = request.params.get("description", "")

    datastream = request.params["file"].file

    doc_list = request.db.docs
    grid = GridFS(request.db)
    id = doc_list.insert(dict(title=title, description=description,
                         created=created, version=5,
                         raw_data=grid.put(datastream)))

    settings = request.registry.settings
    try:
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        socket.connect("tcp://%(plugin.registry.host)s:%(plugin.events.broker.in.p"
                    "ort)s" % settings)
        socket.setsockopt(zmq.LINGER, 100)
        socket.send("new " + str(id), zmq.NOBLOCK)
        socket.close()
    except Exception, e:
        print e

    return dict(id=str(id))


@doc_service.get()
def get(request):
    id_ = request.matchdict["docid"][0]
    doc = request.db.docs.find_one({"_id": ObjectId(id_)})
    grid = GridFS(request.db)

    response = Response(grid.get(doc["raw_data"]).read())
    if "content_type" in doc:
        response.content_type = doc["content_type"]
    return response

plugins_service = Service(name="plugins", path="/plugins")


@plugins_service.put()
def register(request):
    settings = request.registry.settings
    data = json.loads(request.body)
    print data
    assert data["version"] == 1
    return dict(couch_conn=settings["mongodb.url"],
                couch_db_name=settings["mongodb.db_name"],
                subscribe_conn="tcp://%(plugin.registry.host)s:%(plugin.events"
                ".broker.out.port)s" % settings)
