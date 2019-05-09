import datetime
import json
import os
import shutil
from decimal import Decimal

from geoalchemy2.shape import to_shape
from shapely.geometry import mapping

from RealEstateORM.orm_main import *

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
        self.area1 = None
        self.area2 = None
        self.kitchen_area1 = None
        self.kitchen_area2 = None
        self.living_area1 = None
        self.living_area2 = None
        # User polygon
        self.boundary = None
        # Distances
        self.dpark1 = None
        self.dpark2 = None
        self.dmetro1 = None
        self.dmetro2 = None
        self.dkad1 = None
        self.dkad2 = None
        self.dschool1 = None
        self.dschool2 = None
        self.dkindergarten1 = None
        self.dkindergarten2 = None

        self.limit = None
        self.distinct_on_address = None


class QueryBuilder:
    def __init__(self, session, qoptions):
        self.session = session
        self.qoptions = qoptions

        self.query = None

    def range_filter(self, attribute, gte, lte):
        if lte is not None:
            self.query = self.query.filter(attribute <= lte)
        if gte is not None:
            self.query = self.query.filter(attribute >= gte)

    def boundary_filter(self):
        if not(self.qoptions.boundary is None or self.qoptions.boundary.is_empty):
            bound_wkt = self.qoptions.boundary.wkt
            bound = 'SRID=4326; {}'.format(bound_wkt)
            self.query = self.query.filter(AddressView.geom.ST_Within(bound))

    def set_distinct_on_address(self):
        if self.qoptions.distinct_on_address:
            self.query = self.query.distinct(AddressView.address_id)

    def build(self):
        opts = self.qoptions
        query = self.session.query(PriceHistory, Flat, AddressView)
        query = query.join(Flat, Flat.id == PriceHistory.flat_id)
        query = query.join(AddressView, AddressView.id == Flat.address_id)

        self.query = query

        self.range_filter(PriceHistory.observe_date, opts.date1, opts.date2)
        self.range_filter(PriceHistory.price, opts.price1, opts.price2)
        self.range_filter(Flat.qrooms, opts.qrooms1, opts.qrooms2)
        self.range_filter(Flat.area, opts.area1, opts.area2)
        self.range_filter(Flat.kitchen_area, opts.kitchen_area1, opts.kitchen_area2)
        self.range_filter(Flat.living_area, opts.living_area1, opts.living_area2)

        self.range_filter(AddressView.kad, opts.dkad1, opts.dkad2)
        self.range_filter(AddressView.parks, opts.dpark1, opts.dpark2)
        self.range_filter(AddressView.metro, opts.dmetro1, opts.dmetro2)
        self.range_filter(AddressView.school, opts.dschool1, opts.dschool2)
        self.range_filter(AddressView.kindergarten, opts.dkindergarten1, opts.dkindergarten2)

        self.boundary_filter()

        self.set_distinct_on_address()

        self.query = self.query.limit(opts.limit)

    @classmethod
    def create_query(cls, session, qoptions):
        instance = cls(session, qoptions)
        instance.build()
        return instance.query


class Listing:
    def __init__(self):
        self.observe_date = None
        self.price = None

        self.flat_id = None
        self.qrooms = None
        self.floor = None
        self.area = None
        self.kitchen_area = None
        self.living_area = None
        self.description = None
        self.link = None
        self.separate_wc_count = None
        self.combined_wc_count = None

        self.ru_address = None
        self.geom = None
        self.material_type = None
        self.year = None
        self.floors = None

    def geojson_item(self):
        """
        Returns JSON serializable dictionary of attributes.
        :return: dict
        """
        item = dict()
        item['type'] = "Feature"

        geometry = None
        properties = {}
        for k, v in self.__dict__.items():
            if v is not None and k == 'geom':
                geometry = mapping(to_shape(v))
                continue
            elif isinstance(v, Decimal):
                v = float(v)
            elif isinstance(v, MaterialTypeEnum):
                v = v.name
            elif isinstance(v, datetime.date):
                v = str(v)
            properties[k] = v

        item['geometry'] = geometry
        item['properties'] = properties
        return item

    def __repr__(self):
        return 'Listing(flat_id={}, observe_date={}, price={})'.format(self.flat_id, self.observe_date, self.price)


class ListingsGetter:
    _ORMS = (PriceHistory, Flat, AddressView)

    def __init__(self, session, qoptions):
        self.query = QueryBuilder.create_query(session, qoptions)
        self.listings = None

    def orms_attribute_search(self, attr):
        for mapping in self._ORMS:
            try:
                attr_val = getattr(mapping, attr)
                return attr_val
            except AttributeError:
                pass
        message = 'Attribute "{}" does not exist in this ORMs: {}'.format(attr, ', '.join(
            mapping.__name__ for mapping in self._ORMS))
        raise AttributeError(message)

    def set_iterator(self):
        def to_listing(items):
            listing = Listing()
            [setattr(listing, attr, item) for attr, item in zip(values, items)]
            return listing

        def iterator():
            for row in self.query.values(*orm_values):
                yield to_listing(row)

        values = sorted(Listing().__dict__.keys())
        orm_values = [self.orms_attribute_search(v) for v in values]

        self.listings = iterator()

    @classmethod
    def get_listings(cls, session, qoptions):
        instance = cls(session, qoptions)
        instance.set_iterator()
        return instance.listings


def query_to_geojson(session, qoptions):
    listings = ListingsGetter.get_listings(session, qoptions)

    listings = [listing.geojson_item() for listing in listings]

    geojson = dict()
    geojson['type'] = 'FeatureCollection'
    # WGS84
    geojson['crs'] = {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
        }
    }
    geojson['features'] = listings

    return len(listings), json.dumps(geojson, ensure_ascii=False)


def save_query(session, qoptions, ftype='.shp'):
    filename = 'RealEstate_%s' % datetime.datetime.now().strftime('%Y%m%d_%H%M')
    temp_folder_path = os.path.join(DIRNAME, 'uploads', filename)
    os.makedirs(temp_folder_path, exist_ok=True)

    ftype = '.geojson'

    qoptions.limit = 1000
    if ftype.lower() == '.shp':
        raise NotImplemented('Sorry not available')
    elif ftype.lower() == '.geojson':
        count, data = query_to_geojson(
            session,
            qoptions,
        )
        path = os.path.join(temp_folder_path, filename + '.geojson')
        open(path, 'w', encoding='utf8').write(data)
    shutil.make_archive(temp_folder_path, 'zip', temp_folder_path)
    shutil.rmtree(temp_folder_path)
    return temp_folder_path + '.zip'
