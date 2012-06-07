BROKER_URL = 'mongodb://localhost'
CELERY_RESULT_BACKEND = 'mongodb'
CELERY_IMPORTS = ("scanned_docs.plugins.tika", )
