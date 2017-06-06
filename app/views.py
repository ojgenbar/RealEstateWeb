# -*- coding: utf-8 -*-
import os.path
from app import app
from flask import request, send_from_directory
import json
from queryFunc import QueryOptions, query_to_geojson, save_query
import time
import datetime
from shapely.geometry import MultiPolygon, Polygon, shape

DIRNAME = os.path.dirname(__file__)
os.chdir(DIRNAME)


@app.errorhandler(404)
def not_found(error):
    return 'Ошибка: 404 %s' % error


@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return open(os.path.join(DIRNAME, 'index.html')).read()


def qoptions_from_request(args):
    qoptions = QueryOptions()

    print args['bound']
    polygons = [Polygon(shape(i['geometry'])) for i in json.loads(args['bound'])['features'] if i['geometry']["type"] == "Polygon"]
    qoptions.boundary = MultiPolygon(polygons)

    qoptions.date1 = datetime.date(*(int(i) for i in args['date1'].split('-')))
    qoptions.date2 = datetime.date(*(int(i) for i in args['date2'].split('-')))
    try:
        qoptions.price1 = float(args['price1'])
    except ValueError:
        pass
    try:
        qoptions.price2 = float(args['price2']) or None
    except ValueError:
        pass
    try:
        qoptions.area1 = float(args['area1'])
    except ValueError:
        pass
    try:
        qoptions.area2 = float(args['area2'])
    except ValueError:
        pass
    try:
        qoptions.price_sqm1 = float(args['price_sqm1'])
    except ValueError:
        pass
    try:
        qoptions.price_sqm2 = float(args['price_sqm2'])
    except ValueError:
        pass
    try:
        qoptions.qrooms1 = int(args['qrooms1'])
    except ValueError:
        pass
    try:
        qoptions.qrooms2 = int(args['qrooms2'])
    except ValueError:
        pass
    try:
        qoptions.dmetro1 = int(args['dmetro1'])
    except ValueError:
        pass
    try:
        qoptions.dmetro2 = int(args['dmetro2'])
    except ValueError:
        pass
    try:
        qoptions.dmetro1 = int(args['dmetro1'])
    except ValueError:
        pass
    try:
        qoptions.dmetro2 = int(args['dmetro2'])
    except ValueError:
        pass
    try:
        qoptions.dkad1 = int(args['dkad1'])
    except ValueError:
        pass
    try:
        qoptions.dkad2 = int(args['dkad2'])
    except ValueError:
        pass
    # try:
    #     qoptions.dpark1 = int(args['dpark1'])
    # except ValueError:
    #     pass
    try:
        qoptions.dpark2 = int(args['dpark2'])
    except ValueError:
        pass

    # qoptions.floor1 = float(args['floor1']) or None
    # qoptions.floor2 = float(args['floor2']) or None
    # qoptions.floors1 = float(args['floors1']) or None
    # qoptions.floors2 = float(args['floors2']) or None
    # qoptions.kitchen_area1 = args['kitchen_area1'] or None
    # qoptions.kitchen_area2 = args['kitchen_area2'] or None
    # qoptions.living_area1 = args['living_area1'] or None
    # qoptions.living_area2 = args['living_area2'] or None
    # qoptions.building_types = args['building_types'] or None
    # qoptions.bathrooms = args['bathrooms'] or None
    # qoptions.abilities = args['abilities'] or None
    # qoptions.agency = args['agency'] or None
    # qoptions.districts = args['districts'] or None

    qoptions.prettify()
    print qoptions
    return qoptions


@app.route('/query')
def query():
    tstart = time.time()
    args = request.args
    qoptions = qoptions_from_request(args)
    count, res = query_to_geojson(qoptions, maxcount=500)
    print '_'*120
    print 'Count: %s' % count
    print 'Query time: %s sec.' % (time.time()-tstart)
    # print sorted([i for i in dir(qoptions) if not i.startswith('_')])

    return res


@app.route('/download')
def download():
    args = request.args
    qoptions = qoptions_from_request(args)

    uploads = os.path.join(os.path.dirname(DIRNAME), 'uploads')
    export_format = args['exportFormat']
    if export_format == 'ESRI Shapefile':
        export_ext = '.shp'
    elif export_format == 'GeoJSON':
        export_ext = '.geojson'
    else:
        raise ValueError('Unknown export format')

    filename = os.path.basename(save_query(qoptions, ftype=export_ext))
    print '\n%s\n%s\n' % (uploads, filename)
    return send_from_directory(directory=uploads, filename=filename, as_attachment=True)
