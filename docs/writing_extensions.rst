.. _writing_extensions:

Writing extensions
******************

Lembrar is meant to be extended.
It utilizes :term:`setuptools entrypoints` to look for possible plugins.

Lembrar comes with two plugins, so you can have a look at our own :py:func:`setup` method in setup.py

.. code-block:: python
   :emphasize-lines: 7,8

    def setup(
        name="lembrar",
        .
        .
        .
        entry_points="""
        [lembrar.parsers]
        tika = scanned_docs.plugins.tika:parser
        """)

Lembrar stores content in mongodb. You can easily access objects directly there. But there are some consistency checks which you would have to write on your own.
Also, it would be your responsability to check compatibility with future versions of lembrar. 
Only minor version number changes guarantee no changes in the database structure.

Lembrar provides a small API which does all necessary consistency checks.

Your method gets called with a list of docids and a flag, whether to search for all unparsed documents on your own.

Here is a minimum working example::

    from lembrar.db import get_doc_db

    def parser(docids=[], initial=True):
        docdb = get_doc_db(prefix = 'test')
        for docid in docids:
            doc = docdb.find_one(docid)
            doc.update_plugin_attr('test', 'hello world')
            doc.register_searchable_field('test')
            doc.reindex()
            doc.finish_parsing('1.0')

And here is the full API:

.. autofunction:: scanned_docs.db.get_doc_db(prefix)

.. autoclass:: scanned_docs.db.Doc()
    :members: