# -*- coding: utf-8 -*-

from lxml import etree
from pymongo.objectid import ObjectId
from tempfile import NamedTemporaryFile
from webhelpers import text as texthelpers
import argparse
import gevent
import gridfs
import itertools
import json
import pymongo
import requests
import subprocess
import zmq
from celery.task import task

from scanned_docs.index import index
from scanned_docs.utils import convertStringToDateTime

@task
def parser_task():
    return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scanner_subscribe")
    parser.add_argument("--tikapath")
    parser.add_argument("--accepted_languages")
    parser.add_argument("--fill_queue")
    args = parser.parse_args()
    conns = register(args.scanner_subscribe)
    db = open_db_connection(conns["couch_conn"], conns["couch_db_name"])
    print "Registered"
    if args.fill_queue:
        handle_initial(db, args)
    else:
        job = gevent.spawn(subscribe, conns["subscribe_conn"],
                           handle_subscription, db, args)
        job.join()


def register(subscribe_url):
    return json.loads(requests.put(subscribe_url, json.dumps(dict(name="Tika",
                      description="Tika parser", version=1))).content)


def open_db_connection(db_conn, db_name):
    conn = pymongo.Connection(db_conn)
    return conn[db_name]


def subscribe(
    subscription_url,
    handler,
    db,
    args,
    ):

    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect(subscription_url)
    # socket.setsockopt(zmq.SUBSCRIBE, "new")
    while True:
        data = socket.recv()
        key = " ".join(data.split(" ")[1:])
        print "subscription", key
        handle_update(db, args, key)


def handle_initial(db, args):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(args.fill_queue)
    for doc in db.docs.find({"tika_version": {"$exists": False}}):
        print doc["_id"]
        socket.send("new " + str(doc["_id"]))


def handle_subscription():
    pass


def handle_update(db, args, id):
    id = ObjectId(id)
    grid = gridfs.GridFS(db)
    doc = db.docs.find_one(dict(_id=id))
    data = grid.get(doc["raw_data"]).read()
    with NamedTemporaryFile() as tmpfile:
        tmpfile.write(data)
        tmpfile.seek(0)
        cmd = subprocess.Popen(["/usr/bin/java", "-jar", args.tikapath,
                               tmpfile.name], stdout=subprocess.PIPE)
        analysis = cmd.communicate()[0]
        tree = etree.fromstring(analysis)
        namespaces = dict(html="http://www.w3.org/1999/xhtml")

        content_type = \
            tree.xpath("//html:meta[@name=\"Content-Type\"]/@content",
                       namespaces=namespaces)
        date = tree.xpath("//html:meta[@name=\"Creation-Date\"]/@content",
                          namespaces=namespaces)
        if date:
            date = convertStringToDateTime(date[0])
        content = tree.xpath("//html:body/*", namespaces=namespaces)
        if content:
            content = "".join([etree.tostring(x) for x in content])
        text = " ".join(tree.xpath("//*/text()", namespaces=namespaces))
        text = texthelpers.replace_whitespace(text.replace("\n", " ")).strip()
        description = texthelpers.truncate(text, 100, "", whole_word=True)

        def update_with_prefix(key, value):
            db.docs.update({"_id": id}, {"$set": {"tika_" + key: value}})

        def update_if_not_set(key, value):
            db.docs.update({"_id": id, key: {"$exists": False}},
                           {"$set": {key: value}})
            update_with_prefix(key, value)

        def push(key, value):
            db.docs.update({"_id": id}, {"$push": {key: value}})

        if content_type:
            update_if_not_set("content_type", content_type[0])
        if date:
            update_if_not_set("created", date)
        if content:
            update_with_prefix("full_html", content)
            push("full_htmls", "tika_full_html")
        if text:
            update_with_prefix("text", text)
            push("fulltext_fields", "tika_text")
        if description:
            update_if_not_set("description", description)
        update_with_prefix("version", 1)

        success = False
        countdown = itertools.count(-10)
        accepted_languages = args.accepted_languages.split(",")
        while not success and countdown.next():
            fulltext_fields = db.docs.find_one({"_id": id},
                    {"fulltext_fields": 1})["fulltext_fields"]
            text_to_index = []
            for fieldname, value in db.docs.find_one({"_id": id},
                    dict(zip(fulltext_fields, [1 for x in
                    fulltext_fields]))).items():
                if fieldname != "_id":
                    text_to_index.append(value)
            indexed_text = list(index(" ".join(text_to_index),
                                accepted_languages=accepted_languages))
            update_result = db.docs.update({"_id": id,
                    "fulltext_fields": fulltext_fields},
                    {"$set": {"search_terms": indexed_text}}, safe=True)
            success |= update_result["updatedExisting"]
    print "Updated", id
