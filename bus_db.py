# -*- coding: utf-8 -*-
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/pyshp')
import shapefile

import logging
#logger = logging.getLogger('peewee')
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())

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
    route = ForeignKeyField(RouteTable, related_name='busroute')
    stopName = TextField(index=True)
    stopNameKana = TextField()
    lat = FloatField(index=True)
    long = FloatField(index=True)

    class Meta:
        database = database_proxy


class BusStopOrder(Model):
    stopOrder = IntegerField()
    route= ForeignKeyField(RouteTable, related_name='orderroute')
    busStop= ForeignKeyField(BusStop, related_name='orderbusstop')
    duration = IntegerField()

    class Meta:
        database = database_proxy


class BusStopRelation(Model):
    busStopFrom = ForeignKeyField(BusStop, related_name='relation_from_busstop')
    busStopTo = ForeignKeyField(BusStop, related_name='relation_to_busstop')
    distance = FloatField()

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
    database_proxy.create_tables([MetaData, BusStop, BusStopOrder, BusStopRelation, TimeTable, TimeTableItem], True)

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

def _import_time_table(route, bus_stop_order, date_type, timetables):
    for t in timetables:
        timerow = TimeTable.create(
            route = route,
            dateType = date_type
        )
        # バス停毎の到着時間
        for s in t:
            busstop = bus_stop_order[s['busstopIx'] + 1]
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
    dataid = []
    query = MetaData.select().where(
        (MetaData.dataName == meta['dataName'])
    ).execute()
    for row in query:
        dataid.append(row.id)

    # 既存データの削除
    routeid = []
    query = RouteTable.select().where(
        (RouteTable.metaData << dataid)
    ).execute()
    for row in query:
        routeid.append(row.id)

    BusStop.delete().filter(
        (BusStop.route << routeid)
    ).execute()

    BusStopOrder.delete().filter(
        (BusStopOrder.route << routeid)
    ).execute()

    query = TimeTable.select().where(
        (TimeTable.route << routeid)
    ).execute()
    timetableid = []
    for row in query:
        timetableid.append(row.id)
    TimeTableItem.delete().filter(
        (TimeTableItem.timeTable << timetableid)
    ).execute()

    TimeTable.delete().filter(
        (TimeTable.route << routeid)
    ).execute()

    RouteTable.delete().filter(
        (RouteTable.metaData << dataid)
    ).execute()

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


def _subBusStopTime(fromTime, toTime):
    fromTimeBuf = fromTime.split(':')
    toTimeBuf = toTime.split(':')
    fromMin = int(fromTimeBuf[0]) * 60 + int(fromTimeBuf[1])
    toMin = int(toTimeBuf[0]) * 60 + int(toTimeBuf[1])
    if fromMin > toMin:
        #日付が逆転している場合は24h時間を加える
        toMin = toMin + 24*60
    return toMin - fromMin


def _getBusStopTimeDuration(fromBusStopInfo, toBusStopInfo, ix):
    flg = False
    for f in fromBusStopInfo:
        fid = f['id']
        for t in toBusStopInfo:
            if fid + ix == t['id'] and f['timetableId'] == t['timetableId']:
                flg = True
                break
        if flg:
            break
    if not flg:
        raise Exception('_getBusStopTimeDuration', 'unexpected data')
    return _subBusStopTime(f['time'], t['time'])


def import_bus(meta_id, operation_company, line_name, shape, src_srid, timetables):
    with database_proxy.transaction():
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
            bus_stop_order = {}
            for b in timetable['bus_stops']:
                row = BusStop.create(
                    route = route,
                    stopName = b['stopName'],
                    stopNameKana = b['stopNameKana'],
                    lat = b['lat'],
                    long = b['long']
                )
                for o in b['stopOrder']:
                    bus_stop_order[o] = row

            ix = 0
            fromBusStopInfo = None
            for o, row in bus_stop_order.items():
                durationFromStart = 0
                busStopInfo = []
                timeIx = 0
                # スタート開始駅からの到着時間の差を求める
                for t in timetable['weekday_timetable']:
                    # バス停毎の到着時間
                    for s in t:
                        busStopInfo.append({'id': s['busstopIx'], 'time': s['time'], 'timetableId' : timeIx})
                    timeIx += 1
                if ix == 0:
                    fromBusStopInfo = busStopInfo
                else:
                    durationFromStart = _getBusStopTimeDuration(fromBusStopInfo, busStopInfo, ix)
                orderrow = BusStopOrder.create(
                    route = route,
                    busStop = row,
                    stopOrder = o,
                    duration = durationFromStart
                )
                ix += 1
            _import_time_table(route, bus_stop_order, 0, timetable['weekday_timetable'])
            _import_time_table(route, bus_stop_order, 1, timetable['saturday_timetable'])
            _import_time_table(route, bus_stop_order, 2, timetable['holyday_timetable'])


def update_busstop_realtion(distance):
    BusStopRelation.delete().execute()

    database_proxy.get_conn().execute(
        """
        insert into 
            BusStopRelation(busStopFrom_id, busStopTo_id, distance)
        select
            t1.id,
            t2.id,
            POW(ABS(t1.long - t2.long) / 0.0111, 2) + POW(ABS(t1.lat - t2.lat) / 0.0091, 2) as distance 
        from 
            busstop as t1
        inner join busstop as t2 on t1.id <> t2.id and t1.route_id <> t2.route_id
        where distance <= ?
        """,
        (
            distance,
        )
    )


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
            'BusStopOrder' : [],
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
    query = BusStopOrder.select(BusStopOrder, BusStop, RouteTable).where(
        (BusStopOrder.route << routes.keys())
    ).join(RouteTable).switch(BusStopOrder).join(BusStop, on=(BusStop.id==BusStopOrder.busStop)).order_by(BusStopOrder.stopOrder)
    for r in query:
        routes[r.route.id]['BusStopOrder'].append({
            'order': r.stopOrder,
            'busStopId': r.busStop.id
        })

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
            'busStopId' : r.busStop.id,
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


def get_near_bus_stop(long, lat, distance, limit):
    """
    指定のポイントに近いバス停
    """
    sub = 'SQRT(POW(ABS(%f - long) / 0.0111, 2) + POW(ABS(%f - lat) / 0.0091, 2))' % (long, lat)
    filter = 'sub<=%f' % distance
    query = BusStop.select(
        BusStop.id,
        BusStop.stopName,
        RouteTable.id,
        RouteTable.routeName,
        R(sub).alias('sub')
    ).distinct().join(RouteTable).where(R(filter)).order_by(R('sub')).limit(limit)
    ret = []
    for r in query:
       ret.append({
           'id' : r.id,
           'distance' : r.sub
       })
    return ret


def find_route(from_route, to_route, current_route, max_route):
    """
    ルートAとルートBの経路
    """
    # 3経路以上の
    if len(current_route) >= max_route:
        return None

    if from_route == to_route:
        return [[from_route] + current_route]

    current_route = [from_route] + current_route
    connect_ids = get_connect_route(from_route)
    res = []
    for cnn in connect_ids:
        if cnn in current_route:
            continue
        r = find_route(cnn, to_route, current_route, max_route)
        if not r is None:
            res.append(r)
    if len(res) == 0:
        return None
    return res

def get_connect_route(route_id):
    """
    指定のルートに接続しているルート
    """
    rows = database_proxy.get_conn().execute("""
        select 
          distinct
          b2.route_id
        from 
          busStopRelation
        inner join BusStop as b1 
          ON b1.id = busStopFrom_id
        inner join BusStop as b2
          ON b2.id = busStopTo_id
        where
          b1.route_id = ?
    """, (route_id,))
    ret = []
    for r in rows:
        ret.append(r[0])
    return ret


def get_bus_stop_cost(from_bus_stop, to_bus_stop):
    """
    指定のバス停間の乗車時間
    """
    rows = database_proxy.get_conn().execute("""
    select (t2.duration-t1.duration) as cost  from 
      busstoporder as t1
      inner join busstoporder as t2
        on (t1.route_id = t2.route_id and t2.stopOrder > t1.stopOrder)
    where 
      t1.busstop_id = ? and
      t2.busstop_id = ?
    order by t2.stopOrder
    """ , (from_bus_stop, to_bus_stop,))
    
    for r in rows:
        return r[0]

def get_bus_stop_route_connect(bus_stop):
    """
    指定のバス停を含むルートで乗り換え可能なバス亭の一覧
    """
    # costは乗降時間(t2.duration-t1.duration) + 100mあたり1分半として計算
    rows = database_proxy.get_conn().execute("""
    select 
      busStopFrom_id, busStopTo_id, route_id, min(cost) as cost
    from (
    select distinct
      busStopFrom_id, 
      busStopTo_id, 
      ConnectBusStop.route_id  as route_id,
      ((t2.duration-t1.duration) + (distance * 100 * 1.5)) as cost
    from 
      busstoporder as t1
      inner join busstoporder as t2
        on (t1.route_id = t2.route_id and t2.stopOrder > t1.stopOrder)
      inner join BusStopRelation
        on (t2.busStop_id == BusStopRelation.busStopFrom_id)
      inner join BusStop as ConnectBusStop
        on (BusStopRelation.busStopTo_id == ConnectBusStop.id)
    where 
      t1.busstop_id = ?
    ) group  by route_id
    """ , (bus_stop,))
    ret = []
    for r in rows:
        ret.append({ 'transfer_from': r[0], 'transfer_to': r[1], 'route_id': r[2], 'cost': r[3]})
    return ret


def get_bus_route_min_cost(from_bus_stop, to_bus_stop, current_route = [], max_stop = 6, current_cost = 0, min_cost = 9999999):
    """
    乗っている時間が最も少ないルート検索
    """
    if len(current_route) == 0:
        current_route = [from_bus_stop]
    if len(current_route) > max_stop:
        return None, 9999999
    cost = get_bus_stop_cost(from_bus_stop, to_bus_stop)
    if not cost is None:
        if (current_cost + cost) < min_cost:
            return current_route + [to_bus_stop], current_cost + cost
        else:
            # このパスは最低コストを下回らない
            return None, 9999999
    connects = get_bus_stop_route_connect(from_bus_stop)
    min_route = None
    for cnn in connects:
        if cnn['transfer_from'] in current_route:
            continue
        if cnn['transfer_to'] in current_route:
            continue
        route, cost = get_bus_route_min_cost(
            cnn['transfer_to'],
            to_bus_stop,
            current_route + [cnn['transfer_from'], cnn['transfer_to']],
            max_stop,
            current_cost + cnn['cost'],
            min_cost
        )
        if route is None:
            continue
        if min_cost > cost:
            min_cost = cost
            min_route = route
    return min_route, min_cost


def get_bus_route_min_trasfer(from_bus_stop, to_bus_stop, current_route = [], max_stop = 6, current_cost = 0, min_transfer = 9999999, min_cost = 9999999):
    """
    乗り換えが最も少ないルート検索
    """
    if len(current_route) == 0:
        current_route = [from_bus_stop]
    if len(current_route) > max_stop:
        return None, 9999999
    if len(current_route) > min_transfer:
        return None, 9999999
    cost = get_bus_stop_cost(from_bus_stop, to_bus_stop)
    if not cost is None:
        if len(current_route + [to_bus_stop]) < min_transfer:
            return current_route + [to_bus_stop], current_cost + cost
        else:
            # このパスは最低コストを下回らない
            return None, 9999999
    connects = get_bus_stop_route_connect(from_bus_stop)
    min_route = None
    for cnn in connects:
        if cnn['transfer_from'] in current_route:
            continue
        if cnn['transfer_to'] in current_route:
            continue
        route, cost = get_bus_route_min_trasfer(
            cnn['transfer_to'],
            to_bus_stop,
            current_route + [cnn['transfer_from'], cnn['transfer_to']],
            max_stop,
            current_cost + cnn['cost'],
            min_transfer,
            min_cost
        )
        if route is None:
            continue
        if min_transfer > len(route):
            min_transfer = len(route)
            min_cost = cost
            min_route = route
        elif min_transfer == len(route) and min_cost > cost:
            min_cost = cost
            min_route = route
    return min_route, min_cost


def find_bus_route_by_pos(long_from, lat_from, long_to, lat_to, distance, limit):
    fromBusStop = get_near_bus_stop(long_from, lat_from, distance, limit)
    toBusStop = get_near_bus_stop(long_to, lat_to, distance, limit)
    results = []
    fix = 0
    tix = 0
    for f in fromBusStop:
        tix = 0
        for t in toBusStop:
            route, cost = get_bus_route_min_trasfer(f['id'], t['id'])
            if not route is None:
                cost += f['distance'] * 100 * 1.5;
                cost += t['distance'] * 100 * 1.5;
                results.append({'route': route, 'cost' : cost })
            tix += 1
        fix += 1
    min_route = 999999
    min_route_cost = 999999
    min_r = None
    for r in results:
        if len(r['route']) < min_route:
            min_r = r
            min_route = len(r['route'])
            min_route_cost = r['cost']
        if len(r['route']) == min_route:
            # 等しい場合はcostをチェック
            if r['cost'] < min_route_cost:
                min_r = r
                min_route = len(r['route'])
                min_route_cost = r['cost']
    if min_r is None:
        return {}
    ret = {
        'cost' : min_r['cost'],
        'route' : []
    }
    if not min_r is None:
        for r in min_r['route']:
            bus = BusStop.get(BusStop.id == r)
            ret['route'].append({
                'stopId' : bus.id,
                'stopName' : bus.stopName,
                'lat' : bus.lat,
                'long' : bus.long,
                'routeId' : bus.route.id,
                'routeName' : bus.route.routeName
            })
    return ret
