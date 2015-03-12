# coding=utf-8
from bottle import get, post, template, request, Bottle, response, redirect, abort
from json import dumps
import os
import json
from collections import defaultdict
import time
import cgi
import urllib
import kokudo_db
import peewee
import math
import gsi_api


app = Bottle()


def setup(conf):
    global app
    kokudo_db.connect(conf.get('database', 'path'), conf.get('database', 'mod_path'), conf.get('database', 'sep'))
    gsi_api.setup(conf.get('gsi_database', 'path'))


@app.get('/')
def Home():
    return template('home').replace('\n', '')


def _create_geojson(ret):

    res = {'type': 'FeatureCollection', 'features': []}
    for r in ret:
        item = {
            'type': 'Feature',
            'geometry': json.loads(r['geometry']),
            'properties': {}
        }
        for k, i in r.items():
            if not k == 'geometry':
                item['properties'][k] = i
        res['features'].append(item)
    return res


def _str_isfloat(str):
    """
    floatに変換できるかチェック
    """
    try:
        float(str)
        return True
    except ValueError:
        return False


def _check_parameter_geometry(swlng, swlat, nelng, nelat, maxrange):
    """
    ジオメトリー用のパラメータのチェック
    """
    if (not _str_isfloat(swlat) or
        not _str_isfloat(swlng) or
        not _str_isfloat(nelat) or
        not _str_isfloat(nelng)):
        return 'wrong parameter type'

    if ((math.fabs(float(swlat) - float(nelat)) + math.fabs(float(swlng) - float(nelng))) > maxrange):
        return 'wrong parameter range'
    return None


@app.get('/json/get_administrative_district')
def get_administrative_district():
    prefectureName = request.query.prefectureName
    subPrefectureName = request.query.subPrefectureName
    countyName = request.query.countyName
    cityName = request.query.cityName
    administrativeAreaCode = request.query.administrativeAreaCode

    ret = kokudo_db.get_administrative_district_route(prefectureName, subPrefectureName, countyName, cityName, administrativeAreaCode)

    response.content_type = 'application/json;charset=utf-8'
    res = _create_geojson(ret)
    return json.dumps(res)


@app.get('/json/get_administrative_district_by_geometry')
def get_administrative_district_by_geometry():
    swlat = request.query.swlat
    swlng = request.query.swlng
    nelat = request.query.nelat
    nelng = request.query.nelng
    err = _check_parameter_geometry(swlng, swlat, nelng, nelat, 999999)
    response.set_header('Access-Control-Allow-Origin', '*')

    if err:
        response.content_type = 'application/json;charset=utf-8'
        response.status = 400
        return json.dumps({'message': err})

    swlat = float(swlat)
    swlng = float(swlng)
    nelat = float(nelat)
    nelng = float(nelng)

    ret = kokudo_db.get_administrative_district_by_geometry(swlng, swlat, nelng, nelat)

    response.content_type = 'application/json;charset=utf-8'
    res = _create_geojson(ret)
    return json.dumps(res)


@app.get('/json/get_bus_route_by_geometry')
def get_bus_route_by_geometry():
    swlat = float(request.query.swlat)
    swlng = float(request.query.swlng)
    nelat = float(request.query.nelat)
    nelng = float(request.query.nelng)
    ret = kokudo_db.get_bus_route_by_geometry(swlng, swlat, nelng, nelat)

    response.content_type = 'application/json;charset=utf-8'
    res = _create_geojson(ret)
    return json.dumps(res)


@app.get('/json/get_bus_route')
def get_bus_route():
    bsc = request.query.bsc
    boc = request.query.boc
    bln = request.query.bln
    rpd = request.query.rpd
    rps = request.query.rps
    rph = request.query.rph
    rmk = request.query.rmk

    ret = kokudo_db.get_bus_route(bsc, boc, bln, rpd, rps, rph, rmk)

    response.content_type = 'application/json;charset=utf-8'
    res = _create_geojson(ret)
    return json.dumps(res)


@app.get('/json/get_railroad_section_by_geometry')
def get_railroad_section_by_geometry():
    swlat = float(request.query.swlat)
    swlng = float(request.query.swlng)
    nelat = float(request.query.nelat)
    nelng = float(request.query.nelng)
    ret = kokudo_db.get_railroad_section_by_geometry(swlng, swlat, nelng, nelat)

    response.content_type = 'application/json;charset=utf-8'
    res = _create_geojson(ret)
    return json.dumps(res)


@app.get('/json/get_railroad_section')
def get_railroad_section():
    railwayType = request.query.railwayType
    serviceProviderType = request.query.serviceProviderType
    railwayLineName = request.query.railwayLineName
    operationCompany = request.query.operationCompany

    embed_elevation = False
    if request.query.embed_elevation:
        embed_elevation = True

    ret = kokudo_db.get_railroad_section(railwayType, serviceProviderType, railwayLineName, operationCompany)

    response.content_type = 'application/json;charset=utf-8'
    response.set_header('Access-Control-Allow-Origin', '*')

    res = _create_geojson(ret)
    if embed_elevation:
        res = gsi_api.convert_geojson(res)
    return json.dumps(res)


@app.get('/json/get_station_by_geometry')
def get_station_by_geometry():
    swlat = float(request.query.swlat)
    swlng = float(request.query.swlng)
    nelat = float(request.query.nelat)
    nelng = float(request.query.nelng)
    ret = kokudo_db.get_station_by_geometry(swlng, swlat, nelng, nelat)

    response.content_type = 'application/json;charset=utf-8'
    res = _create_geojson(ret)
    return json.dumps(res)


@app.get('/json/get_station')
def get_station():
    railwayType = request.query.railwayType
    serviceProviderType = request.query.serviceProviderType
    railwayLineName = request.query.railwayLineName
    operationCompany = request.query.operationCompany
    stationName = request.query.stationName
    ret = kokudo_db.get_station(railwayType, serviceProviderType, railwayLineName, operationCompany, stationName)

    response.content_type = 'application/json;charset=utf-8'
    res = _create_geojson(ret)
    return json.dumps(res)


@app.get('/json/get_pos_by_address')
def get_pos_by_address():
    """
    住所から座標を取得する
    """
    address_list = request.query.address_list
    ret = kokudo_db.convert_addresslist_to_pos(address_list)
    response.content_type = 'application/json;charset=utf-8'
    res = _create_geojson(ret)
    return json.dumps(res)


@app.get('/json/get_sediment_disaster_hazard_area_surface_by_geometry')
def get_sediment_disaster_hazard_area_surface_by_geometry():
    swlat = float(request.query.swlat)
    swlng = float(request.query.swlng)
    nelat = float(request.query.nelat)
    nelng = float(request.query.nelng)
    ret = kokudo_db.get_sediment_disaster_hazard_area_surface_by_geometry(swlng, swlat, nelng, nelat)

    response.content_type = 'application/json;charset=utf-8'
    res = _create_geojson(ret)
    return json.dumps(res)


@app.get('/json/get_sediment_disaster_hazard_area_line_by_geometry')
def get_sediment_disaster_hazard_area_line_by_geometry():
    swlat = float(request.query.swlat)
    swlng = float(request.query.swlng)
    nelat = float(request.query.nelat)
    nelng = float(request.query.nelng)
    ret = kokudo_db.get_sediment_disaster_hazard_area_line_by_geometry(swlng, swlat, nelng, nelat)

    response.content_type = 'application/json;charset=utf-8'
    res = _create_geojson(ret)
    return json.dumps(res)


@app.get('/json/get_sediment_disaster_hazard_area_point_by_geometry')
def get_sediment_disaster_hazard_area_point_by_geometry():
    swlat = float(request.query.swlat)
    swlng = float(request.query.swlng)
    nelat = float(request.query.nelat)
    nelng = float(request.query.nelng)
    ret = kokudo_db.get_sediment_disaster_hazard_area_point_by_geometry(swlng, swlat, nelng, nelat)

    response.content_type = 'application/json;charset=utf-8'
    res = _create_geojson(ret)
    return json.dumps(res)


@app.get('/json/get_expected_flood_area_by_geometry')
def get_expected_flood_area_by_geometry():
    swlat = float(request.query.swlat)
    swlng = float(request.query.swlng)
    nelat = float(request.query.nelat)
    nelng = float(request.query.nelng)
    ret_geo, ret_attr = kokudo_db.get_expected_flood_area_by_geometry(swlng, swlat, nelng, nelat)

    response.content_type = 'application/json;charset=utf-8'
    res = _create_geojson(ret_geo)
    return json.dumps({
        'geojson' : res, 
        'attribute' : ret_attr
    })


@app.get('/json/get_gust_by_geometry')
def get_gust_by_geometry():
    swlat = float(request.query.swlat)
    swlng = float(request.query.swlng)
    nelat = float(request.query.nelat)
    nelng = float(request.query.nelng)
    ret = kokudo_db.get_gust_by_geometry(swlng, swlat, nelng, nelat)

    response.content_type = 'application/json;charset=utf-8'
    return json.dumps(ret)
