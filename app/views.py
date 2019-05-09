# -*- coding: utf-8 -*-
import os.path
import traceback

from app import app
from flask import request, send_from_directory
import json
from query_functions import QueryOptions, query_to_geojson, save_query
from RealEstateORM.connection import create_local_session
import time
import datetime
from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.ops import cascaded_union
import shutil


DIRNAME = os.path.dirname(__file__)
UPLOADS_DIR = os.path.join(os.path.dirname(DIRNAME), 'uploads')
DATE_FORMAT = '%Y-%m-%d'
MAX_COUNT = 500

os.chdir(DIRNAME)
session = create_local_session(user='web_app')


@app.errorhandler(404)
def not_found(error):
    return 'Ошибка: 404 %s' % error


@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    with open(os.path.join(DIRNAME, 'index.html'), encoding='utf-8') as f:
        page = f.read()
    return page


def _multipolygon_from_geojson(data):
    features = json.loads(data)['features']
    polygons = [Polygon(shape(feature['geometry'])) for feature in features if feature['geometry']["type"] == "Polygon"]
    boundary = cascaded_union(polygons)
    return boundary


def _date_from_string(s):
    return datetime.datetime.strptime(s, DATE_FORMAT).date()


def _price_from_string(s):
    return float(s)*1000


ARGUMENTS_FUNCS = {
    'boundary': _multipolygon_from_geojson,
    'date1': _date_from_string,
    'date2': _date_from_string,
    'price1': _price_from_string,
    'price2': _price_from_string,
    'area1': float,
    'area2': float,
    'kitchen_area1': float,
    'kitchen_area2': float,
    'living_area1': float,
    'living_area2': float,
    'price_sqm1': _price_from_string,
    'price_sqm2': _price_from_string,
    'qrooms1': int,
    'qrooms2': int,
    'dmetro1': int,
    'dmetro2': int,
    'dkad1': int,
    'dkad2': int,
    'dpark2': int,
    'dschooll': int,
    'dschool2': int,
    'dkindergarten1': int,
    'dkindergarten2': int,
    'exportFormat': str,
}


def qoptions_from_request(args):
    qoptions = QueryOptions()

    for key, value in args.items():
        func = ARGUMENTS_FUNCS[key]
        value = func(value) if value != '' else None
        setattr(qoptions, key, value)

    return qoptions


@app.route('/query')
def query():
    tstart = time.time()
    args = request.args
    qoptions = qoptions_from_request(args)
    qoptions.limit = MAX_COUNT
    qoptions.distinct_on_address = True

    count, res = query_to_geojson(session, qoptions)

    print('_'*120)
    print('Count: %s' % count)
    print('Query time: %s sec.' % (time.time()-tstart))
    # print(sorted([i for i in dir(qoptions) if not i.startswith('_')]))

    return res


@app.route('/download')
def download():
    args = request.args
    qoptions = qoptions_from_request(args)
    qoptions.limit = MAX_COUNT

    export_format = args['exportFormat']
    if export_format == 'ESRI Shapefile':
        export_ext = '.shp'
    elif export_format == 'GeoJSON':
        export_ext = '.geojson'
    else:
        raise ValueError('Unknown export format')

    filename = os.path.basename(save_query(session, qoptions, ftype=export_ext))
    print('\n%s\n%s\n' % (UPLOADS_DIR, filename))
    try:
        clean_uploads_dir()
    except OSError:
        traceback.print_exc()
    return send_from_directory(directory=UPLOADS_DIR, filename=filename, as_attachment=True)


def clean_uploads_dir():
    now = time.time()

    for f in os.listdir(UPLOADS_DIR):
        if not f.startswith('RealEstate_'):
            continue

        path = os.path.join(UPLOADS_DIR, f)
        if now - os.path.getmtime(path) < 60:
            continue

        print('rm {}'.format(f))
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
