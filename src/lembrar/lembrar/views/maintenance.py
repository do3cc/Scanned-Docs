# -*- coding: utf-8 -*-

from datetime import datetime
from guess_language import guessLanguage
from lembrar.index import index


def upgrade(request):
    doc_list = request.db.docs
    for doc in doc_list.find():
        if "version" not in doc:
            doc["version"] = 1
            doc["created"] = datetime.utcnow()
        doc_list.save(doc)
    for doc in doc_list.find({"version": 1}):
        if "searchable_text" not in doc.keys():
            doc["version"] = 2
            doc_list.save(doc)
            continue
        searchable_text = doc.pop("searchable_text")
        lang = guessLanguage(searchable_text)
        search_terms = index(searchable_text + " " + doc["title"], [lang])
        doc["search_terms"] = search_terms
        doc["language"] = lang
        doc["version"] = 2
        doc_list.save(doc)
    for doc in doc_list.find({"version": 2}):
        doc["version"] = 3
        doc["search_terms"] = [x.lower() for x in doc["search_terms"]]
        doc_list.save(doc)
    for doc in doc_list.find({"version": 3}):
        doc["version"] = 4
        doc["keywords"] = []
        doc_list.save(doc)
    for doc in doc_list.find({"version": 4}):
        doc["version"] = 5
        doc["already_scanned"] = True
        doc_list.save(doc)
    return {"success": 1}
