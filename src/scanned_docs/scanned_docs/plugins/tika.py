#!/usr/bin/python
# -*- coding: utf-8 -*-
from lxml import etree
from tempfile import NamedTemporaryFile
from webhelpers import text as texthelpers
import pymongo
import subprocess
from celery.task import task
from scanned_docs.utils import convertStringToDateTime
from scanned_docs.db import DocDB
import os


@task
def parser_task(
    docids=None,
    initial=False,
    docdb=None,
    tikapath=None,
    accepted_languages=None,
    ):

    tikapath = tikapath or os.environ.get('tikapath')
    accepted_languages = accepted_languages \
        or os.environ.get('accepted_languages')
    docdb = docdb or DocDB(open_db_connection(), accepted_languages)
    if initial:
        handle_initial(docdb, tikapath, accepted_languages)
        return
    for docid in docids or []:
        handle_update(docdb, tikapath, accepted_languages, docid)
    return


def open_db_connection(db_conn=None, db_name=None):
    db_conn = db_conn or os.environ.get('mongodb_conn')
    db_name = db_name or os.environ.get('mongodb_db')
    conn = pymongo.Connection(db_conn)
    return conn[db_name]


def handle_initial(db, tikapath, accepted_languages):
    for doc in db.find({'tika_version': {'$exists': False}}):
        handle_update(db, tikapath, accepted_languages, doc=doc)


def handle_update(
    db,
    tikapath,
    accepted_languages,
    id=None,
    doc=None,
    ):

    if not doc:
        doc = db.find_one(id)
    data = doc.raw_data
    with NamedTemporaryFile() as tmpfile:
        tmpfile.write(data)
        tmpfile.seek(0)
        cmd = subprocess.Popen(['/usr/bin/java', '-jar', tikapath,
                               tmpfile.name], stdout=subprocess.PIPE)
        analysis = cmd.communicate()[0]
        tree = etree.fromstring(analysis)
        xp = lambda term: tree.xpath(term, namespaces=namespaces)
        namespaces = dict(html='http://www.w3.org/1999/xhtml')
        content_type = xp('//html:meta[@name="Content-Type"]/@content')
        date = xp('//html:meta[@name="Creation-Date"]/@content')
        if date:
            date = convertStringToDateTime(date[0])
        content = xp('//html:body/*')
        if content:
            content = ''.join([etree.tostring(x) for x in content])
        text = ' '.join(xp('//*/text()'))
        text = texthelpers.replace_whitespace(text.replace('\n', ' '
                )).strip()
        description = texthelpers.truncate(text, 100, '',
                whole_word=True)

        if content_type:
            doc.update_plugin_and_canonical('content_type',
                    content_type[0], 'tika')
        if date:
            doc.update_plugin_and_canonical('created', date, 'tika')
        if content:
            doc.update_plugin('full_html', content, 'tika')
            doc.register_html_representation('full_html', 'tika')
        if text:
            doc.update_plugin('text', text, 'tika')
            doc.register_searchable_field("text", "tika")
        if description:
            doc.update_plugin_and_canonical('description', description,
                    'tika')
        doc.update_plugin('version', 1, 'tika')
        doc.reindex()
