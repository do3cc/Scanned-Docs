def test_index():
    from scanned_docs import index
    retval = index.index("These are some tests", ['en'])
    assert set([u'these', u'are', u'some', u'test']) == retval
