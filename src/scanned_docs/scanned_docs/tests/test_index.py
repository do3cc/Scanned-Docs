def test_index():
    from scanned_docs import index
    from pyramid.threadlocal import get_current_registry

    get_current_registry().settings = dict(accepted_languages='de')
    retval = index.index("These are some tests", 'en')
    assert set([u'thes', u'are', u'som', u'test']) == retval
