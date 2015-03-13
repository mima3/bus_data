# coding=utf-8
from bottle import get, post, template, request, Bottle, response, redirect, abort
from json import dumps
import os
import json
from collections import defaultdict
import time
import cgi
import bus_db
import peewee
import math


app = Bottle()


def setup(conf):
    global app
    bus_db.connect(conf.get('database', 'path'), conf.get('database', 'mod_path'), conf.get('database', 'sep'))


@app.get('/')
def Home():
    return 'test'


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


@app.get('/json/get_bus_data')
def get_bus_data():
    operationCompany = request.query.operationCompany
    ret = bus_db.get_bus(operationCompany)
    response.content_type = 'application/json;charset=utf-8'
    return json.dumps(ret)
