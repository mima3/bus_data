# -*- coding: utf-8 -*-
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/pyshp')
import shapefile

import logging
logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

database_proxy = Proxy()  # Create a proxy for our db.


SRID = 4326


class PolygonField(Field):
    db_field = 'polygon'


class PointField(Field):
    db_field = 'point'


class LineStringField(Field):
    db_field = 'linestring'


class MultiPolygonField(Field):
    db_field = 'multipolygon'


class MultiPointField(Field):
    db_field = 'multipoint'


class MultiLineStringField(Field):
    db_field = 'multilinestring'


class MetaData(Model):
    id = PrimaryKeyField()
    dataName = TextField(index=True)
    author = TextField()
    url = TextField()
    license = TextField()

    class Meta:
        database = database_proxy

class RouteTable(Model):
    """
    """
    id = PrimaryKeyField()
    metaData = ForeignKeyField(MetaData, related_name='route_meta')
    operationCompany = TextField(index=True)
    lineName = TextField(index=True)
    route = TextField(index=True)
    routeName = TextField()
    geometry = LineStringField()

    class Meta:
        database = database_proxy


class BusStop(Model):
    """
    """
    route= ForeignKeyField(RouteTable, related_name='busroute')
    stopName = TextField(index=True)
    stopNameKana = TextField()
    lat = FloatField(index=True)
    long = FloatField(index=True)

    class Meta:
        database = database_proxy


class TimeTable(Model):
    """
    """
    route= ForeignKeyField(RouteTable, related_name='timeroute')
    dateType = IntegerField()

    class Meta:
        database = database_proxy


class TimeTableItem(Model):
    """
    """
    timeTable= ForeignKeyField(TimeTable, related_name='timetable')
    busStop = ForeignKeyField(BusStop, related_name='busstop')
    time = TextField()

    class Meta:
        database = database_proxy

def connect(path, spatialite_path, evn_sep=';'):
    """
    データベースへの接続
    @param path sqliteのパス
    @param spatialite_path mod_spatialiteへのパス
    @param env_sep 環境変数PATHの接続文字 WINDOWSは; LINUXは:
    """
    os.environ["PATH"] = os.environ["PATH"] + evn_sep + os.path.dirname(spatialite_path)
    db = SqliteExtDatabase(path)
    database_proxy.initialize(db)
    db.field_overrides = {
        'polygon': 'POLYGON',
        'point': 'POINT',
        'linestring': 'LINESTRING',
        'multipolygon': 'MULTIPOLYGON',
        'multipoint': 'MULTIPOINT',
        'multilinestring': 'MULTILINESTRING',
    }
    db.load_extension(os.path.basename(spatialite_path))


def setup(path, spatialite_path, evn_sep=';'):
    connect(path, spatialite_path, evn_sep)
    database_proxy.create_tables([MetaData, BusStop, TimeTable, TimeTableItem], True)

    database_proxy.get_conn().execute('SELECT InitSpatialMetaData()')
    database_proxy.get_conn().execute("""
        CREATE TABLE IF NOT EXISTS "RouteTable" (
          "id" INTEGER PRIMARY KEY AUTOINCREMENT,
          "metadata_id" INTEGER ,
          "operationCompany" TEXT,
          "lineName" TEXT ,
          "route" TEXT ,
          "routeName" TEXT,
          FOREIGN KEY ("metadata_id") REFERENCES "MetaData" ("id")
        );
    """)
    database_proxy.get_conn().execute("""
        CREATE INDEX IF NOT EXISTS RouteTable_operationCompany ON "RouteTable"("operationCompany");
    """)
    database_proxy.get_conn().execute("""
        CREATE INDEX IF NOT EXISTS RouteTable_metadata_id ON "RouteTable"("metadata_id");
    """)
    database_proxy.get_conn().execute("""
        CREATE INDEX IF NOT EXISTS RouteTable_lineName ON "RouteTable"("lineName");
    """)
    database_proxy.get_conn().execute("""
        Select AddGeometryColumn ("RouteTable", "Geometry", ?, "LINESTRING", 2);
    """, (SRID,))

def _import_time_table(route, bus_rows, date_type, timetables):
    for t in timetables:
        timerow = TimeTable.create(
            route = route,
            dateType = date_type
        )
        # バス停毎の到着時間
        for s in t:
            busstop = bus_rows[s['busstop']]
            TimeTableItem.create(
                 timeTable = timerow,
                 busStop = busstop,
                 time = s['time']
            )

def _makeGeometryString(type, shape):
    r = type + '('
    i = 0
    for d in shape.points:
        if i > 0:
            r += ','
        r = r + ('%f %f' % (d[0], d[1]))
        i += 1
    r += ')'
    return r

def import_meta(meta):
    MetaData.delete().filter(
        (MetaData.dataName == meta['dataName'])
    ).execute()

    ret = MetaData.create(
      dataName = meta['dataName'],
      author = meta['author'],
      url = meta['url'],
      license = meta['license']
    )
    return ret.id

def import_bus(meta_id, operation_company, line_name, shape, src_srid, timetables):
    with database_proxy.transaction():
        # 既存データの削除
        routeid = []
        query = RouteTable.select().where(
            (RouteTable.operationCompany == operation_company) &
            (RouteTable.lineName == line_name)
        ).execute()
        for row in query:
            routeid.append(row.id)

        BusStop.delete().filter(
            (BusStop.route << routeid)
        ).execute()

        query = TimeTable.select().where(
            (TimeTable.route << routeid)
        ).execute()

        timetableid = []
        for row in query:
            timetableid.append(row.id)
        TimeTableItem.delete().filter(
            TimeTableItem.timeTable << timetableid
        ).execute()

        TimeTable.delete().filter(
            (TimeTable.route << routeid)
        ).execute()

        routedict = {}
        sf = shapefile.Reader(shape)
        shaperec = sf.iterShapeRecords()
        for sr in shaperec:
            routedict[sr.record[0]] = _makeGeometryString('LINESTRING', sr.shape)

        for timetable in timetables:
            database_proxy.get_conn().execute(
                """
                INSERT INTO RouteTable
                  (metaData_id, operationCompany, lineName, route, routeName, geometry)
                VALUES(?, ?,?,?,?,Transform(GeometryFromText(?, ?),?))
                """,
                (
                    meta_id,
                    operation_company,
                    line_name,
                    timetable['route'],
                    timetable['routeName'],
                    routedict[timetable['route']], src_srid, SRID
                )
            )
            route = RouteTable.get(
                (RouteTable.operationCompany==operation_company) &
                (RouteTable.lineName==line_name) &
                (RouteTable.route==timetable['route'])
            )
            bus_rows = {}
            for b in timetable['bus_stops']:
                row = BusStop.create(
                    route = route,
                    stopName = b['stopName'],
                    stopNameKana = b['stopNameKana'],
                    lat = b['lat'],
                    long = b['long']
                )
                bus_rows[b['stopName']] = row
            _import_time_table(route, bus_rows, 0, timetable['weekday_timetable'])
            _import_time_table(route, bus_rows, 1, timetable['saturday_timetable'])
            _import_time_table(route, bus_rows, 2, timetable['holyday_timetable'])


def get_bus(dataName):
    try:
        meta = MetaData.get(
            (MetaData.dataName == dataName)
        )
    except MetaData.DoesNotExist:
        return {}
    rows = database_proxy.get_conn().execute("""
      SELECT
        id,
        lineName,
        route,
        routeName,
        AsGeoJson(geometry)
      FROM
        RouteTable
      WHERE
        metadata_id = ?
    """ , (meta.id,))
    routes = {}
    for r in rows:
        routes[r[0]] = {
            'lineName' : r[1],
            'route' : r[2],
            'routeName' : r[3],
            'geometry' : r[4],
            'BusStop' : {},
            'TimeTable' : {}
        }
    query = BusStop.select(BusStop, RouteTable).where(
        (BusStop.route << routes.keys())
    ).join(RouteTable)
    for r in query:
        routes[r.route.id]['BusStop'][r.id] = {
            'stopName': r.stopName,
            'stopNameKana': r.stopNameKana,
            'lat': r.lat,
            'long': r.long
        }
    query = TimeTable.select(TimeTable, RouteTable).where(
        (TimeTable.route << routes.keys())
    ).join(RouteTable)
    timetableids = {}
    for r in query:
        routes[r.route.id]['TimeTable'][r.id] = {
            'dateType': r.dateType,
            'table' : []
        }
        timetableids[r.id] = r.route.id

    query = (TimeTableItem
        .select(TimeTableItem, TimeTable, BusStop)
        .join(TimeTable)
        .switch(TimeTableItem)
        .join(BusStop, on=(TimeTableItem.busStop == BusStop.id))
        .where(TimeTableItem.timeTable << timetableids.keys())
    )
    for r in query:
        routes[timetableids[r.timeTable.id]]['TimeTable'][r.timeTable.id]['table'].append({
            'busStop' : r.busStop.stopName,
            'time' : r.time
        })
    return {
        "meta" : {
            "dataName" : meta.dataName,
            "author" : meta.author,
            "url" : meta.url,
            "license" : meta.license
        },
        "routes" : routes
    }
