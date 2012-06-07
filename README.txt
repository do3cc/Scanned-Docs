Scanner
=======

A webapp that accepts documents and extracts as much information from them
as possible.

The application works with plugins. Out of process plugins get notified via
ZMQ notifications that new documents exist. These plugins then access the
object directly in the database, and extend the objects with more metadata

Installation
============
The application is built via buildout.
A stock ubuntu 11.10 installation needed the following additional setup to
work:
apt-get install git python-virtualenv mercurial libzmq-dev python-dev libxslt1-dev libevent1-dev

apt-get build-dep python

Usage
=====
The application and controlled via supervisord. The plugins are independent
processes and to speed things up, one can run more of these.
There are some things to take into consideration though:

Due to the way ZMQ works in simple configurations, messages get lost when
processes get killed, and messages get forwared asap.
To handle multiple threads of the webserver, we needed to add a broker for
messages.
The consequences are these:
If you add many documents fast, they get redirected to the workers immediately.
If you want to add more workers, the workers won't get any of the already
submitted messages. If you want the additional workers, you must kill the
broker and all workers. Then start the brokers FIRST, and then the workers.
Now the messages are lost. But the workers write into the database whether they
finished processing a document. Therefor, the workers knows for which documents
a message has to be regenerated.
To do this, one must run another script: ./bin/tika_reset.sh

All scripts need parameters, they all have rudimentary documentation which
won't help alot. But for all scripts exist shell scripts in the same directory
with the same name and an additional .sh suffix. These shell scripts call
the scripts with the correct arguments.

Plugin Development
==================
TODO