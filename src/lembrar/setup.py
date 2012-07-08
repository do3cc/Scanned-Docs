# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.txt")).read()

requires = [
    "argparse",
    "cornice",
    "gevent",
    "guess_language",
    "gunicorn",
    "iso8601",
    "lxml",
    "PasteScript",
    "Pillow",
    "pymongo==2.0.1",
    "celery",
    "pyramid<1.3a0",
    "PyStemmer",
    "python-magic",
    "pyzmq",
    "requests",
    "text_sentence",
    "WebError",
    "WebHelpers",
    ]

test_requires = ["nose", "coverage", "WebTest", "mock"]

setup(
    name="lembrar",
    version="0.0",
    description="lembrar",
    long_description=README,
    classifiers=["Programming Language :: Python", "Framework :: Pylons",
                 "Topic :: Internet :: WWW/HTTP",
                 "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"],
    author="Patrick Gerken",
    author_email="docc@patrick-gerken.de",
    url="http://do3.cc",
    keywords="web pyramid mongodb",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=test_requires,
    extras_require=dict(test=test_requires),
    test_suite="lembrar",
    entry_points="""\
      [paste.app_factory]
      main = lembrar:main
      [console_scripts]
      tika = lembrar.plugins.tika:main
      broker = lembrar.plugins.broker:main
      [lembrar.parsers]
      tika = lembrar.plugins.tika:parser_task
      """,
    paster_plugins=["pyramid"],
    )
