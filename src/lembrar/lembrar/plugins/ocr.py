#!/usr/bin/python
# -*- coding: utf-8 -*-
from lxml import etree
from tempfile import NamedTemporaryFile
from webhelpers import text as texthelpers
import subprocess
from celery.task import task
from lembrar.utils import convertStringToDateTime
from lembrar.db import get_doc_db
from lembrar.recognize import recognize
import os
from pyramid.threadlocal import get_current_registry


def parser(docids=[], initial=False):
    parser_task.delay(docids, initial)


@task
def parser_task(
    docids=None,
    initial=False,
    docdb=None,
    accepted_languages=None,
    ):
    version = '0.1'
    settings = get_current_registry().settings
    accepted_languages = accepted_languages \
        or (os.environ.get('accepted_languages')
            or settings.get('accepted_languages')).split(',')
    docdb = get_doc_db(prefix='ocr')
    if initial:
        for docid in docdb.find_unparsed(version):
            handle_update(docid, accepted_languages, version)
    for docid in docids or []:
        handle_update(docdb, docid, accepted_languages, version)
    return


def handle_update(
    db,
    id,
    accepted_languages,
    version,
    ):

    doc = db.find_one(id)
    data = doc.raw_data

    lang, ignore, searchterms = recognize(data, accepted_languages, False)
    doc.update_plugin_and_canonical_attr('language', lang)
    doc.update_plugin('ocr', searchterms)
    doc.register_searchable_field('ocr')
    doc.finish_parsing(version)
    doc.reindex()