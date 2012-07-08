from bson.binary import Binary
from datetime import datetime
from pyramid.httpexceptions import HTTPFound, HTTPServerError

from lembrar.image import get_images_from_stream, get_thumbnail
from lembrar.index import index
from lembrar.recognize import recognize


def human_add(request):
    if request.method.lower() == 'post':
        return add(request)
    return {}


def add(request):
    title = request.params['title']
    created = request.params.get('created', datetime.utcnow()) or \
        datetime.utcnow()
    description = request.params.get('description', '')
    force_detection = request.params.get("force_detection",
                                         'true').lower() == 'true'
    accepted_languages = request.registry.settings['accepted_languages']

    imgstream = request.params['file'].file

    doc_list = request.db.docs

    for image in get_images_from_stream(imgstream):
        try:
            lang, img, text = recognize(image, accepted_languages,
                                        force_detection)
        except TypeError, e:
            err_msg = "Error: " + str(e)
            request.session.flash(err_msg, 'failure')
            return HTTPServerError(explanation=err_msg,
                                   detail='Go back, unselect force '\
                                       'detection, and try again')
        text += " " + description + " " + title
        if text:
            search_terms = list(index(text, [lang]))
        else:
            search_terms = ''
        thumb = get_thumbnail(image)

        doc_list.insert({'img': Binary(image),
                         'thumb': Binary(thumb),
                         'created': created,
                         'version': 4,
                         'forced_detection': force_detection,
                         'language': lang,
                         'keywords': [],
                         'search_terms': search_terms,
                         'title': title})

    url = request.resource_url(request.context)
    request.session.flash("Document added", 'success')
    return HTTPFound(location=url)
