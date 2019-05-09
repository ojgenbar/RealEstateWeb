# -*- coding: utf-8 -*-
from app import app
from gevent.pywsgi import WSGIServer
import sys

host = '0.0.0.0'
port = 16224
try:
    port = int(sys.argv[1])
except (ValueError, IndexError):
    pass

print('Started at port={}, host={}'.format(port, host))

http_server = WSGIServer((host, port), app)
http_server.serve_forever()
