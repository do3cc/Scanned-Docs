#!/usr/bin/python
# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
from pkg_resources import resource_filename

config = ConfigParser()
filename = resource_filename('lembrar', '../../../buildout.cfg')
config.read(filename)
