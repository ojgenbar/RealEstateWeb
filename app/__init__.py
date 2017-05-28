# -*- coding: utf-8 -*-


from flask import Flask, url_for
from flask_cors import CORS, cross_origin

# app = Flask(__name__,
#             static_path='/static',
#             root_path='/static')
app = Flask(__name__)
from app import views
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# app.use_x_sendfile = True
# print app.root_path

# print url_for('static', filename='favicon.ico')

