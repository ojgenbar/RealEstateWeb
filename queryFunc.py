# -*- coding: utf-8 -*-
import sys
import time
from datetime import date
from datetime import datetime
import json
import os
import shutil

tstart = time.time()
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'RealEstateORM'))
from ORMBase import session, Flat, District, Price_history, Address
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping, Polygon
import shapefile


DIRNAME = os.path.dirname(__file__)


class QueryOptions:
    def __init__(self):
        self.date1 = None
        self.date2 = None
        self.price1 = None
        self.price2 = None
        self.qrooms1 = None
        self.qrooms2 = None
        self.price_sqm1 = None
        self.price_sqm2 = None
        self.floor1 = None
        self.floor2 = None
        self.floors1 = None
        self.floors2 = None
        self.area1 = None
        self.area2 = None
        self.kitchen_area1 = None
        self.kitchen_area2 = None
        self.living_area1 = None
        self.living_area2 = None
        self.building_types = None
        self.bathrooms = None
        self.abilities = None
        self.agency = None
        self.districts = None
        self.boundary = None

    def prettify(self):
        if self.date1 or self.date2:
            if not self.date1:
                self.date1 = date(2016, 1, 1)
            if not self.date2:
                self.date2 = datetime.now().date()

        if self.price1 or self.price2:
            if not self.price1:
                self.price1 = 0
            if not self.price2:
                self.price2 = 1000000

        if self.qrooms1 or self.qrooms2:
            if not self.qrooms1:
                self.qrooms1 = 0
            if not self.qrooms2:
                self.qrooms2 = 100

        if self.price_sqm1 or self.price_sqm2:
            if not self.price_sqm1:
                self.price_sqm1 = 0
            if not self.price_sqm2:
                self.price_sqm2 = 1000000

        if self.floor1 or self.floor2:
            if not self.floor1:
                # Как в "Незнайке на Луне".
                self.floor1 = -10
            if not self.floor2:
                self.floor2 = 1000

        if self.floors1 or self.floors2:
            if not self.floors1:
                # Как в "Незнайке на Луне".
                self.floors1 = -10
            if not self.floors2:
                self.floors2 = 1000

        if self.living_area1 or self.living_area2:
            if not self.living_area1:
                self.living_area1 = 0.0
            if not self.living_area2:
                self.living_area2 = 1000000

        if self.kitchen_area1 or self.kitchen_area2:
            if not self.kitchen_area1:
                self.kitchen_area1 = 0.0
            if not self.kitchen_area2:
                self.kitchen_area2 = 1000000


class Listing:
    def __init__(self):
        self.id = None
        self.observe_date = None
        self.geom = None
        self.qrooms = None
        self.district = None
        self.ru_address = None
        self.en_address = None
        self.floor = None
        self.floors = None
        self.building_type = None
        self.area = None
        self.living_area = None
        self.kitchen_area = None
        self.bathroom = None
        self.price = None
        self.price_sqm = None
        self.abilities = None
        self.agency = None
        self.tel = None
        self.description = None
        self.bn_id = None
        self.link = None
        self.ad_type = None

    def to_dict(self):
        d = dict()
        d['type'] = "Feature"
        geometry = json.loads(json.dumps(mapping(self.geom)), encoding='UTF8')
        properties = dict()
        properties['id'] = self.id
        properties['observe_date'] = self.observe_date.strftime("%Y-%m-%d")
        properties['qrooms'] = self.qrooms
        properties['district'] = self.district
        properties['ru_address'] = self.ru_address
        properties['en_address'] = self.en_address
        properties['floor'] = self.floor
        properties['floors'] = self.floors
        properties['building_type'] = self.building_type
        properties['area'] = self.area
        properties['living_area'] = self.living_area
        properties['kitchen_area'] = self.kitchen_area
        properties['bathroom'] = self.bathroom
        properties['price'] = self.price
        properties['price_sqm'] = self.price_sqm
        properties['abilities'] = self.abilities
        properties['agency'] = self.agency
        properties['tel'] = self.tel
        properties['description'] = self.description
        properties['bn_id'] = self.bn_id
        properties['link'] = self.link

        d['geometry'] = geometry
        d['properties'] = properties
        return d

    def __repr__(self):
        message = list()
        message.append(u'ID="%s"' % self.id)
        message.append(u'date="%s"' % self.observe_date)
        message.append(u'district="%s"' % self.district)
        message.append(u'address="%s"' % self.ru_address)
        message.append(u'rooms="%s"' % self.qrooms)
        message.append(u'area="%.1f"' % self.area)
        message.append(u'price="%.1f"' % self.price)
        message.append(u'price_sqm="%.1f"' % self.price_sqm)
        message = u"<Type 'Listing' (%s)>" % u', '.join(message)
        return message.encode(sys.stdout.encoding or 'utf-8', errors='ignore')


def reorganize_result(qres):
    ph = qres[0]
    flat = qres[1]
    addr = qres[2]
    distr = qres[3]

    res = Listing()
    res.ru_address = addr.ru_address
    res.en_address = addr.en_address
    res.geom = to_shape(addr.geom)
    res.building_type = addr.building_type
    res.floors = addr.floors
    res.district = distr.name
    res.id = flat.id
    res.qrooms = flat.qrooms
    res.floor = flat.floor
    res.area = float(flat.area)
    res.kitchen_area = flat.kitchen_area
    res.living_area = flat.living_area
    res.bathroom = flat.bathroom
    res.abilities = flat.abilities
    res.agency = flat.agency
    res.tel = flat.tel
    res.description = flat.description
    res.bn_id = flat.bn_id
    res.ad_type = flat.ad_type
    res.link = flat.link
    res.observe_date = ph.observe_date
    res.price = float(ph.price)
    res.price_sqm = float(ph._price_sqm)
    return res


def build_query(qoptions):
    qoptions.prettify()
    query = session.query(Price_history, Flat, Address, District)
    if qoptions.date1:
        query = query.filter(Price_history.observe_date >= qoptions.date1,
                             Price_history.observe_date <= qoptions.date2)
    if qoptions.price1:
        query = query.filter(Price_history.price >= qoptions.price1,
                             Price_history.price <= qoptions.price2)
    if qoptions.price_sqm1:
        query = query.filter(Price_history._price_sqm >= qoptions.price_sqm1,
                             Price_history._price_sqm <= qoptions.price_sqm2)

    query = query.join(Flat, Flat.id == Price_history.flat_id)

    if qoptions.qrooms1:
        query = query.filter(Flat.qrooms >= qoptions.qrooms1,
                             Flat.qrooms <= qoptions.qrooms2)
    if qoptions.floor1:
        query = query.filter(Flat.floor >= qoptions.floor1,
                             Flat.floor <= qoptions.floor2)
    if qoptions.area1:
        query = query.filter(Flat.area >= qoptions.area1,
                             Flat.area <= qoptions.area2)
    # if qoptions.living_area1:
    #     query = query.filter(Flat.living_area >= qoptions.living_area1,
    #                          Flat.living_area <= qoptions.living_area2)
    # if qoptions.kitchen_area1:
    #     query = query.filter(Flat.kitchen_area >= qoptions.kitchen_area1,
    #                          Flat.kitchen_area <= qoptions.kitchen_area2)
    if qoptions.abilities:
        query.filter(Flat.abilities.in_(qoptions.abilities))
    if qoptions.agency:
        query.filter(Flat.agency.in_(Flat.agency))
    if qoptions.bathrooms:
        query = query.filter(Flat.bathroom.in_(qoptions.bathrooms))

    query = query.join(Address, Address.id == Flat.address_id)
    if qoptions.boundary:
        bound_wkt = qoptions.boundary.wkt
        bound = 'SRID=4326; %s' % bound_wkt
        # print bound
        query = query.filter(Address.geom.ST_CoveredBy(bound))
    if qoptions.building_types:
        query = query.filter(Address.building_type.in_(qoptions.building_types))
    if qoptions.floors1:
        query = query.filter(Address.floors >= qoptions.floors1,
                             Address.floors <= qoptions.floors2)
    query = query.join(District, District.id == Address.district_id)
    if qoptions.districts:
        query = query.filter(District.name.in_(qoptions.districts))
    return query


def query_to_geojson(qoptions, maxcount=None):

    query = build_query(qoptions)

    res = []

    if maxcount:
        query = query.limit(maxcount)

    elements = query.all()

    for elem in elements:
        listing = reorganize_result(elem)
        res.append(listing.to_dict())

    res_dict = dict()
    res_dict['type'] = 'FeatureCollection'
    # WGS84
    res_dict['crs'] = {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
        }
    }
    res_dict['features'] = res
    return query.count(), json.dumps(res_dict)


def query_to_shp(qoptions, path, maxcount=None):
    path = os.path.abspath(path)
    name, ext = os.path.splitext(path)
    lowext = ext.lower()
    if lowext == '.shp':
        path = name

    query = build_query(qoptions)
    res = []

    writer = shapefile.Writer(shapefile.POINT)
    writer.autoBalance = 1

    # Создание атрибутов.
    writer.field('ID', 'N', '10')
    writer.field('QROOMS', 'N', '2')
    writer.field('DISTR', 'C', '40')
    writer.field('RUADDRESS', 'C', '100')
    writer.field('ENADDRESS', 'C', '200')
    writer.field('FLOOR', 'N', '10')
    writer.field('FLOORS', 'N', '10')
    writer.field('PROJ_TYPE', 'C', '40')
    writer.field('AREA', 'N', '40')
    writer.field('LIVING_AREA', 'C', '40')
    writer.field('KITCHEN_AREA', 'C', '40')
    writer.field('BATHROOM', 'C', '40')
    writer.field('PRICE', 'N', '10')
    writer.field('PRICESQM', 'N', '13')
    writer.field('ADDCOND', 'C', '40')
    writer.field('AGENCY', 'C', '40')
    writer.field('PHONE', 'C', '40')
    writer.field('DESCRIPTION', 'C', '200')
    writer.field('DATE', 'C', '20')
    writer.field('ADTYPE', 'N', '2')
    writer.field('BNID', 'N', '10')
    writer.field('LINK', 'C', '200')

    if maxcount:
        query = query.limit(maxcount)

    elements = query.all()

    for elem in elements:
        listing = reorganize_result(elem)
        geom = list(listing.geom.coords)[0]
        writer.point(*geom)
        writer.record(
            ID=listing.id,
            QROOMS=listing.qrooms,
            DISTR=listing.district.encode('utf-8'),
            RUADDRESS=listing.ru_address.encode('utf-8'),
            ENADDRESS=listing.en_address.encode('utf-8'),
            FLOOR=listing.floor,
            FLOORS=listing.floors,
            PROJ_TYPE=listing.building_type.encode('utf-8'),
            AREA=listing.area,
            LIVING_AREA=listing.living_area.encode('utf-8'),
            KITCHEN_AREA=listing.kitchen_area.encode('utf-8'),
            BATHROOM=listing.bathroom.encode('utf-8'),
            PRICE=listing.price,
            PRICESQM=listing.price_sqm,
            ADDCOND=listing.abilities.encode('utf-8'),
            AGENCY=listing.agency.encode('utf-8'),
            PHONE=listing.tel.encode('utf-8'),
            DESCRIPTION=listing.description.encode('utf-8'),
            DATE=listing.observe_date.strftime('%Y-%m-%d'),
            ADTYPE=listing.ad_type,
            BNID=listing.bn_id,
            LINK=listing.link.encode('utf-8')
        )

    writer.save(path + '.shp')
    open(path + '.prj', 'w')\
        .write('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]')


def save_query(qoptions, ftype='.shp'):
    filename = 'RealEstate_%s' % datetime.now().strftime('%Y%m%d_%H%M')
    temp_folder_path = os.path.join(DIRNAME, 'uploads', filename)
    try:
        os.mkdir(temp_folder_path)
    except OSError:
        pass
    if ftype.lower() == '.shp':
        query_to_shp(qoptions,
                     os.path.join(temp_folder_path, filename),
                     maxcount=10000)
    shutil.make_archive(temp_folder_path, 'zip', temp_folder_path)
    shutil.rmtree(temp_folder_path)
    return temp_folder_path + '.zip'


if __name__ == '__main__':

    # tstart = time.time()
    ####################
    reader = shapefile.Reader(r'wf/in/bound.shp')
    pol = Polygon(reader.shape(0).points)
    print pol.wkt

    qo = QueryOptions()
    qo.date1 = date(2017, 2, 3)
    qo.date2 = date(2017, 2, 3)
    # qo.price1 = 2500
    # qo.price2 = 3500
    # qo.qrooms1 = 1
    # qo.qrooms2 = 2
    # qo.price_sqm1 = 10
    # qo.price_sqm2 = 400
    # qo.floor1 = 4
    # qo.floor2 = 6
    # qo.area1 = 1
    # qo.area2 = 90
    # qo.building_types = [u'К', u'БР', u'Б/М', u'К/М']
    # qo.bathrooms = [u'Р', u'С']
    # qo.districts = [u'Область', u'Калининский район']
    qo.boundary = pol
    # print re_query(qo)[1]
    # print re_query(qo)[0]
    print os.path.join(os.path.dirname(os.path.dirname(__file__)), 'RealEstateORM')

    ####################
    print '_' * 50
    print 'Time of working: %s sec.' % str(time.time() - tstart).zfill(10)
