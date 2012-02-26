#!/usr/bin/python
# -*- coding: utf-8 -*-
from pymongo.objectid import ObjectId
import argparse
import json
import socket
import zmq
import requests
import pymongo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scanner_subscribe')
    args = parser.parse_args()
    conns = register(args.scanner_subscribe)
    db = open_db_connection(conns['couch_conn'], conns['couch_db_name'])
    subscribe(conns['subscribe_conn'], handle_subscription, db)
    handle_initial(db)


def register(subscribe_url):
    return json.loads(requests.put(subscribe_url, json.dumps(dict(name='Tika', description='Tika parser', version=1))).content)


def open_db_connection(db_conn, db_name):
    conn = pymongo.Connection(db_conn)
    return conn[db_name]

def subscribe(subscription_url, handler, db):
    pass

def handle_initial(db):
    for doc in db.docs.find({'tika.state': {'$exists': False}}):
        handle_update(db, doc['_id'])

def handle_subscription():
    pass

def handle_update(db, id):
    data = db.docs.find_one(dict(_id=ObjectId(id)))['img']
    conn = socket.create_connection(('127.0.0.1', 2222))
    conn.send(data)
    print conn.recv(1000000)
    import pdb;pdb.set_trace()