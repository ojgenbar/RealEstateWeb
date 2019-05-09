# -*- coding: utf-8 -*-
from app import app
from gevent.pywsgi import WSGIServer

# app.run(debug=False, port=1624)
http_server = WSGIServer(('127.0.0.1', 1624), app)
http_server.serve_forever()
