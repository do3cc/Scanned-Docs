#!/usr/bin/python
# -*- coding: utf-8 -*-
from lxml import etree
from tempfile import NamedTemporaryFile
from webhelpers import text as texthelpers
import subprocess
from celery.task import task
from lembrar.utils import convertStringToDateTime
from lembrar.db import get_doc_db
import os
from magic import from_buffer as magic_buffer


def parser(docids=[], initial=False):
    parser_task.delay(docids, initial)


@task
def parser_task(
    docids=None,
    initial=False,
    docdb=None,
    ):
    version = '0.1'
    docdb = get_doc_db(prefix='mimetype')
    if initial:
        for docid in docdb.find_unparsed(version):
            handle_update(docid, version)
    for docid in docids or []:
        handle_update(docdb, docid, version)
    return


def handle_update(
    db,
    id,
    version,
    ):
    print "doing it"
    doc = db.find_one(id)
    data = doc.raw_data
    magic = magic_buffer(data, mime=True)
    doc.update_plugin_and_canonical_attr('mimetype', magic)
    doc.finish_parsing(version)
    doc.reindex()
