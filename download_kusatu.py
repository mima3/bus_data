# -*- coding: utf-8 -*-
import urllib
import grequests
import os
import zipfile
import sys

download_path = 'download'

def save_local(res):
    path = os.path.join(download_path, os.path.basename(res.url))
    with open(path, 'wb') as f:
        for chunk in res.iter_content(1024):
            f.write(chunk)

def expand_zip(res):
    path = os.path.join(download_path, os.path.basename(res.url))
    with open(path, 'wb') as f:
        for chunk in res.iter_content(1024):
            f.write(chunk)
    with zipfile.ZipFile(path, 'r') as zip_file:
        zip_file.extractall(path=download_path)


def main(argvs, argc):
    if argc != 2:
        print ("Usage #python %s download_folder" % argvs[0])
        return 1
    download_path = argvs[1]
    srcs = {
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M01_stop_times.xlsx' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M01_stops_ccw.csv' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M01_shapes.zip' : expand_zip,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M02_stop_times.xlsx' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M02_stops_ib.csv' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M02_stops_ob.csv' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M02_shapes.zip' : expand_zip,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M03_stop_times.xlsx' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M03_stops_cw.csv' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M03_stops_ccw.csv' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M03_shapes.zip' : expand_zip,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M04_stop_times.xlsx' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M04_stops_cw.csv' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M04_stops_ccw.csv' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M04_shapes.zip' : expand_zip,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M05_stop_times.xlsx' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M05_stops_cw.csv' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M05_stops_ccw.csv' : save_local,
        'http://www.city.kusatsu.shiga.jp/kurashi/kotsudorokasen/mamebus/opendata.files/M05_shapes.zip' : expand_zip
    }
    rs = (grequests.get(u) for u in srcs.keys())
    g = grequests.imap(rs)
    for r in g:
        if r.status_code != 200:
            raise Exception('Download failed.', r.url, r.status_code)
        srcs[r.url](r)


if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    sys.exit(main(argvs, argc))