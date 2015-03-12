#!C:\Python27\python.exe
# coding: utf-8
from bottle import run
import ConfigParser
import sys


conf = ConfigParser.SafeConfigParser()
conf.read("C:\\pleiades-e3.6\\xampp\\htdocs\\kokudo\\application.ini")
try:
  i = 0
  path = conf.get('system', 'path' + str(i))
  while path != "":
    i = i + 1
    sys.path.append(path)
    path = conf.get('system', 'path' + str(i))
except ConfigParser.NoOptionError as e:
  pass

from application import app, setup
setup(conf)

run(app, server='cgi')
