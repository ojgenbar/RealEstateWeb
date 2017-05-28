# -*- coding: utf-8 -*-
import os.path
from app import app
from flask import request, send_from_directory
import json
from queryFunc import QueryOptions, query_to_geojson, save_query
import datetime
from shapely.geometry import MultiPolygon, Polygon, shape

DIRNAME = os.path.dirname(__file__)
os.chdir(DIRNAME)


@app.errorhandler(404)
def not_found(error):
    return 'Ошибка: 404 %s' % error


def qoptions_from_request(args):
    qoptions = QueryOptions()

    print args['bound']
    polygons = [Polygon(shape(i['geometry'])) for i in json.loads(args['bound'])['features'] if i['geometry']["type"] == "Polygon"]
    qoptions.boundary = MultiPolygon(polygons)

    qoptions.date1 = datetime.date(*(int(i) for i in args['date1'].split('-')))
    qoptions.date2 = datetime.date(*(int(i) for i in args['date2'].split('-')))
    qoptions.price1 = args['price1'] or None
    qoptions.price2 = args['price2'] or None

    qoptions.prettify()
    return qoptions


@app.route('/query')
def query():
    args = request.args
    qoptions = qoptions_from_request(args)
    count, res = query_to_geojson(qoptions, maxcount=500)
    print 'Count: %s' % count
    print sorted([i for i in dir(qoptions) if not i.startswith('_')])
    return res


@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return open(os.path.join(DIRNAME, 'index.html')).read()


@app.route('/download')
def download():
    args = request.args
    qoptions = qoptions_from_request(args)

    uploads = os.path.join(os.path.dirname(DIRNAME), 'uploads')

    filename = os.path.basename(save_query(qoptions))
    print '\n%s\n%s\n' % (uploads, filename)
    return send_from_directory(directory=uploads, filename=filename, as_attachment=True)


@app.route('/api')
def js():
    data = open(r'wf/q1.geojson').read()
    return data


# if __name__ == '__main__':
#     re_query()
