# -*- coding: utf-8 -*-
import sys
import os
import csv, codecs, cStringIO

from xlrd import open_workbook
import xlrd
import enum
import zenhan


DataDirection = enum.Enum('DataDirection', 'row col')


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class xlsReader:
    def __init__(self, wbpath, sheetname): 
        self.workbook = open_workbook(wbpath)
        self.sheet = self.workbook.sheet_by_name(sheetname)
        self.dmode = self.workbook.datemode

    def get_cell(self):
        try:
            # 0スタートになる
            v = self.sheet.cell(self.row  - 1, self.col - 1).value
            cty = self.sheet.cell(self.row  - 1, self.col - 1).ctype
            if cty == xlrd.XL_CELL_DATE:
                v = xlrd.xldate_as_tuple(v, self.dmode)
            return v
        except IndexError:
            return None

    def set_offset(self, r, c):
        self.row = r
        self.col = c

    def next_cell(self, direction):
        if DataDirection.row == direction:
            self.row += 1
        else:
            self.col += 1
        return self.row, self.col


def get_bus_timetable(wbname, sheetname, stop_offset_row, stop_offset_col, stopdirection, timetable_offset_row, timetable_offset_col, chk_func):
    xls = xlsReader(wbname, sheetname)
    stop_name_list = []
    if stopdirection == DataDirection.row:
        busdirection = DataDirection.col
    else:
        busdirection = DataDirection.row
    xls.set_offset(stop_offset_row, stop_offset_col)
    while True:
        v = xls.get_cell()
        if not v:
            break
        v = zenhan.h2z(v)
        v = v.replace('\n', '')
        stop_name_list.append(v)
        xls.next_cell(stopdirection)

    buslist = []

    busrow = timetable_offset_row
    buscol = timetable_offset_col
    xls.set_offset(busrow, buscol)

    while True:
        setflg = False
        stoptime = []
        if stopdirection == DataDirection.row:
            busrow = timetable_offset_row
        else:
            buscol = timetable_offset_col
        xls.set_offset(busrow, buscol)
        item = []
        for i in range(len(stop_name_list)):
            v = xls.get_cell()
            if not v:
                busrow, buscol = xls.next_cell(stopdirection)
                continue
            item.append({
              'busstop': stop_name_list[i],
              'busstopIx': i,
              'time': '%02d:%02d' % (v[3], v[4])}
            )
            setflg = True
            busrow, buscol = xls.next_cell(stopdirection)
        if not setflg:
            break
        if chk_func:
            if chk_func(xls.workbook, xls.sheet, busrow, buscol, item):
                buslist.append(item)
        else:
            buslist.append(item)
        busrow, buscol = xls.next_cell(busdirection)
    return buslist

def convert_bus_stop_name(rule, bus_stops):
    for bus_stop in bus_stops:
        if bus_stop['stopName'] in rule:
            bus_stop['stopName'] = rule[bus_stop['stopName']]

def get_bus_stop(csv):
    bus_stops = []
    with open(csv , 'rb') as csvfile:
        reader = UnicodeReader(csvfile, encoding='cp932')
        i = 0
        for row in reader:
            i += 1
            if i == 1:
                #一行目はヘッダー
                continue
            orderstr = row[1].split(',')
            order = []
            for o in orderstr:
                order.append(int(o))

            bus_stops.append({
                'stopOrder' : order,
                'stopName' : row[2],
                'stopNameKana' : row[3],
                'long' : row[6],
                'lat' : row[7]
            })
    return bus_stops
