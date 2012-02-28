# -*- coding: utf-8 -*-

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.renderers import get_renderer
from pyramid.session import UnencryptedCookieSessionFactoryConfig
import pymongo

from scanned_docs.resources import Root


def add_base_template(event):
    base = get_renderer("scanned_docs:templates/base.pt").implementation()
    event.update({"base": base})


def main(global_config, **settings):
    """ This function returns a WSGI application. """

    my_session_factory = UnencryptedCookieSessionFactoryConfig("itsaseekreet")
    config = Configurator(settings=settings, root_factory=Root,
                          session_factory=my_session_factory)
    config.include("cornice")
    config.scan("scanned_docs.service")
    config.add_view("scanned_docs.views.list.list_view",
                    context="scanned_docs:resources.Root",
                    renderer="scanned_docs:templates/list.pt")
    config.add_route("thumb", pattern="{id}/thumb")
    config.add_view("scanned_docs.views.list.thumb", route_name="thumb")
    config.add_route("image", pattern="{id}/image")
    config.add_view("scanned_docs.views.list.image", route_name="image")
    config.add_route("del", pattern="{id}/delete")
    config.add_view("scanned_docs.views.list.delete", route_name="del",
                    renderer="json")
    config.add_view("scanned_docs.views.add.add", name="add",
                    context="scanned_docs:resources.Root", renderer="json")
    config.add_view("scanned_docs.views.add.human_add", name="human_add",
                    context="scanned_docs:resources.Root",
                    renderer="scanned_docs:templates/add.pt")
    config.add_view("scanned_docs.views.maintenance.upgrade", name="upgrade",
                    renderer="json")
    config.add_route("edit", pattern="{id}/edit")
    config.add_view("scanned_docs.views.edit.edit", route_name="edit",
                    renderer="scanned_docs:templates/edit.pt",
                    request_method="GET")
    config.add_view("scanned_docs.views.edit.edit_post", route_name="edit",
                    request_method="POST")
    config.add_static_view("static", "scanned_docs:static")
    config.add_subscriber(add_base_template, "pyramid.events.BeforeRender")

    # MongoDB

    def add_mongo_db(event):
        settings = event.request.registry.settings
        db_name = settings["mongodb.db_name"]
        db = settings["mongodb_conn"][db_name]
        event.request.db = db

    db_uri = settings["mongodb.url"]
    conn = pymongo.Connection(db_uri)
    config.registry.settings["mongodb_conn"] = conn
    db = conn[config.registry.settings["mongodb.db_name"]]
    db.docs.ensure_index("created")
    config.add_subscriber(add_mongo_db, NewRequest)

    # registry

    return config.make_wsgi_app()
