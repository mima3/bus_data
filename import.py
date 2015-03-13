# -*- coding: utf-8 -*-
import ConfigParser
import downloader
import sys
import json
import os
import bus_db
import importer


class BusParserCallBack(object):
    def check_shoutengai_saturday(self, workbook, sheet, busrow, buscol, item):
        if sheet.cell(busrow  - 1, 2 - 1).value:
            return True
        else:
            return False


def main(argvs, argc):
    global download_path
    if argc != 2:
        print ("Usage #python %s download_folder" % argvs[0])
        return 1
    conf = ConfigParser.SafeConfigParser()
    conf.read(argvs[1])
    download = []
    i = 1
    while True:
        try:
          download_path = conf.get('download', 'target' + str(i))
          json_path = conf.get('download', 'json' + str(i))
          with open(json_path, 'r') as f:
              download.append({'target' : download_path, 'json': json.load(f)})
          i += 1
        except ConfigParser.NoOptionError as e:
          break
    bus_db.setup(conf.get('database', 'path'), conf.get('database', 'mod_path'), conf.get('database', 'sep'))
    callback = BusParserCallBack()
    for d in download:
        if not os.path.exists(d['target']):
            os.makedirs(d['target'])
        downloader.download(d['target'], d['json']['download'])
        importer.import_bus(d['target'], d['json']['import_rule'], d['json']['convert_rule'], callback)


if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    sys.exit(main(argvs, argc))

