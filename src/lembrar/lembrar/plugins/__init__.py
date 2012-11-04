#!/usr/bin/python
# -*- coding: utf-8 -*-
from pkg_resources import iter_entry_points


def notify_new_document(docid):
    for entry in iter_entry_points(group='lembrar.parsers'):
        entry.load()(docids=[docid], initial=False)

