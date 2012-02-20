from cornice import Service
from scanned_docs.views.add import add as view_add

doc_service = Service(name='doc', path='/doc')

@doc_service.put()
def add(request):
    return view_add(request)
