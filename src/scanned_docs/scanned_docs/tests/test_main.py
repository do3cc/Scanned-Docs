from pyramid import testing


class test_views(object):
    def setUp(self):
        from scanned_docs import main
        from webtest import TestApp
        app = main({}, **{'mongodb.url': 'localhost:10000',
                          'mongodb.db_name': 'test'})
        self.testapp = TestApp(app)

    def test_home(self):
        assert self.testapp.get('/').status == '200 OK'
