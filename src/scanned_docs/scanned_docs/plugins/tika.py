#!/usr/bin/python
# -*- coding: utf-8 -*-
from lxml import etree
from tempfile import NamedTemporaryFile
from webhelpers import text as texthelpers
import subprocess
from celery.task import task
from scanned_docs.utils import convertStringToDateTime
from scanned_docs.db import get_doc_db
import os


def parser(docids=[], initial=False):
    parser_task.delay(docids, initial)


@task
def parser_task(
    docids=None,
    initial=False,
    docdb=None,
    tikapath=None,
    ):
    version = '0.1'
    tikapath = tikapath or os.environ.get('tikapath')
    docdb = get_doc_db(prefix='tika')
    if initial:
        for docid in docdb.find_unparsed(version):
            handle_update(docid, tikapath, version)
    for docid in docids or []:
        handle_update(docdb, tikapath, version)
    return


def handle_update(
    db,
    id,
    tikapath,
    version,
    ):

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
            doc.update_plugin_and_canonical_attr('content_type',
                    content_type[0])
        if date:
            doc.update_plugin_and_canonical_attr('created', date)
        if content:
            doc.update_plugin_attr('full_html', content)
            doc.register_html_representation('full_html')
        if text:
            doc.update_plugin('text', text)
            doc.register_searchable_field("text")
        if description:
            doc.update_plugin_and_canonical_attr('description', description)
        doc.finish_parsing(version)
        doc.reindex()
