Installation
************
The application is built via buildout.
Buildout takes care of getting the right python packages and creating useful configuration files for the programs needed.
Buildout does not install system programs

Required programs
=================
A stock ubuntu 11.10 installation needed the following additional setup to
work:
apt-get install git python-virtualenv mercurial libzmq-dev python-dev libxslt1-dev libevent1-dev mongodb libjpeg62-dev cuneiform poppler-utils openjdk-7-jre
apt-get build-dep python

.. todo::
    We try to remove the need for libzmq so check again,.

Running buildout
================
There is no buildout.cfg, link
the desired environment to buildout.cfg. Currently there is only development.cfg

Preflight
=========
The buildout installs the tests too. Please run the tests to see if everything
worked:
./bin/nosetests src/scanned_docs

Usage
*****
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

.. todo::
    This ZMQ stuff is outdated, hopefully.
    

All scripts need parameters, they all have rudimentary documentation which
won't help alot. But for all scripts exist shell scripts in the same directory
with the same name and an additional .sh suffix. These shell scripts call
the scripts with the correct arguments.
