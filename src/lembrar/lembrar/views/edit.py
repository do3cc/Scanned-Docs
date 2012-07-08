# -*- coding: utf-8 -*-

from datetime import datetime
from pymongo.objectid import ObjectId
from pyramid.httpexceptions import HTTPFound

from lembrar.index import index


def edit(request):
    doc = request.db.docs.find({"_id": ObjectId(request.matchdict["id"])})[0]
    retval = {}
    for key in ["title"]:
        retval[key] = doc[key]

    retval["created"] = doc["created"].strftime("%Y-%m-%dT%H:%MZ")

    retval["searchterms"] = list(set([x.lower().strip() for x in
                                 doc.get("search_terms", []) if len(x) > 2]))
    retval["searchterms"].sort()
    retval["keywords"] = "\n".join(doc.get("keywords", []))
    retval["distinct_keywords"] = request.db.docs.distinct("keywords")
    retval["docid"] = doc["_id"]
    retval["html_views"] = [doc[x] for x in doc.get("full_htmls", [])]

    return retval


def edit_post(request):
    doc = request.db.docs.find({"_id": ObjectId(request.matchdict["id"])})[0]
    doc["title"] = request.params["title"]
    doc["created"] = datetime.strptime(request.params["created"],
                                       "%Y-%m-%dT%H:%MZ")
    description = request.params["description"]
    if description:
        doc["search_terms"] += index(request.params["description"])
    doc["keywords"] = request.params["keywords"].split()
    request.db.docs.update({"_id": doc["_id"]}, doc)

    url = request.route_url("edit", id=doc["_id"])
    request.session.flash("Changes saved", "success")
    return HTTPFound(location=url)
