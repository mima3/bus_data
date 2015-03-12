# -*- coding: utf-8 -*-
import bus_data_parser
import bus_db
import os


class BusParserCallBack(object):
    def check_shoutengai_saturday(self, workbook, sheet, busrow, buscol, item):
        if sheet.cell(busrow  - 1, 2 - 1).value:
            return True
        else:
            return False

callback = BusParserCallBack()

src = [
    {
        'operation_company' : u'草津市',
        'line_name' : u'商店街循環線',
        'shape' : 'M01_shapes/M01.shp',
        'srid' : 2448 , #JGD2000/平面直角座標系6
        'timetables' : [
            {
                'route' : 'Route1L',
                'bus_stops' : u'M01_stops_ccw.csv',
                'weekday_timetable' : {
                    'workbook' : u'M01_stop_times.xlsx',
                    'sheetname' : u'M01_stop_times',
                    'stop_offset_row' : 6,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 7,
                    'timetable_offset_col' : 3,
                },
                'saturday_timetable' : {
                    'workbook' : u'M01_stop_times.xlsx',
                    'sheetname' : u'M01_stop_times',
                    'stop_offset_row' : 6,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 7,
                    'timetable_offset_col' : 3,
                    'check_func' : 'check_shoutengai_saturday'
                },
                'holyday_timetable' : {
                }
            }
        ]
    },
    {
        'operation_company' : u'草津市',
        'line_name' : u'草津駅医大線',
        'shape' : 'M02_shapes/M02.shp',
        'srid' : 2448 , #JGD2000/平面直角座標系6
        'timetables' : [
            {
                'route' : u'Route2R',
                'bus_stops' : u'M02_stops_ib.csv',
                'weekday_timetable' : {
                    'workbook' : u'M02_stop_times.xlsx',
                    'sheetname' : u'M02_stop_times',
                    'stop_offset_row' : 6,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 7,
                    'timetable_offset_col' : 3,
                },
                'saturday_timetable' : {
                    'workbook' : u'M02_stop_times.xlsx',
                    'sheetname' : u'M02_stop_times',
                    'stop_offset_row' : 6,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 7,
                    'timetable_offset_col' : 3,
                    'check_func' : 'check_shoutengai_saturday'
                },
                'holyday_timetable' : {
                }
            },
            {
                'route' : u'Route2L',
                'bus_stops' : u'M02_stops_ob.csv',
                'weekday_timetable' : {
                    'workbook' : u'M02_stop_times.xlsx',
                    'sheetname' : u'M02_stop_times',
                    'stop_offset_row' : 19,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 20,
                    'timetable_offset_col' : 3,
                },
                'saturday_timetable' : {
                    'workbook' : u'M02_stop_times.xlsx',
                    'sheetname' : u'M02_stop_times',
                    'stop_offset_row' : 19,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 20,
                    'timetable_offset_col' : 3,
                    'check_func' : 'check_shoutengai_saturday'
                },
                'holyday_timetable' : {
                }
            }
        ]
    },
    {
        'operation_company' : u'草津市',
        'line_name' : u'山田線（北山田循環）',
        'shape' : 'M03_shapes/M03.shp',
        'srid' : 2448 , #JGD2000/平面直角座標系6
        'timetables' : [
            {
                'route' : u'Route3R',
                'bus_stops' : u'M03_stops_cw.csv',
                'weekday_timetable' : {
                    'workbook' : u'M03_stop_times.xlsx',
                    'sheetname' : u'M03_stop_times（平日）',
                    'stop_offset_row' : 6,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 7,
                    'timetable_offset_col' : 3,
                },
                'saturday_timetable' : {
                    'workbook' : u'M03_stop_times.xlsx',
                    'sheetname' : u'M03_stop_times（土曜）',
                    'stop_offset_row' : 6,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 7,
                    'timetable_offset_col' : 3,
                },
                'holyday_timetable' : {
                }
            },
            {
                'route' : u'Route3L',
                'bus_stops' : u'M03_stops_ccw.csv',
                'weekday_timetable' : {
                    'workbook' : u'M03_stop_times.xlsx',
                    'sheetname' : u'M03_stop_times（平日）',
                    'stop_offset_row' : 14,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 15,
                    'timetable_offset_col' : 3,
                },
                'saturday_timetable' : {
                    'workbook' : u'M03_stop_times.xlsx',
                    'sheetname' : u'M03_stop_times（土曜）',
                    'stop_offset_row' : 14,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 15,
                    'timetable_offset_col' : 3,
                },
                'holyday_timetable' : {
                }
            }
        ]
    },
    {
        'operation_company' : u'草津市',
        'line_name' : u'山田線（木ノ川循環）',
        'shape' : 'M04_shapes/M04.shp',
        'srid' : 2448 , #JGD2000/平面直角座標系6
        'timetables' : [
            {
                'route' : u'Route4R',
                'bus_stops' : u'M04_stops_cw.csv',
                'weekday_timetable' : {
                    'workbook' : u'M04_stop_times.xlsx',
                    'sheetname' : u'M04_stop_times（平日）',
                    'stop_offset_row' : 6,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 7,
                    'timetable_offset_col' : 3,
                },
                'saturday_timetable' : {
                    'workbook' : u'M04_stop_times.xlsx',
                    'sheetname' : u'M04_stop_times（土曜）',
                    'stop_offset_row' : 6,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 9,
                    'timetable_offset_col' : 3,
                },
                'holyday_timetable' : {
                }
            },
            {
                'route' : u'Route4L',
                'bus_stops' : u'M04_stops_cw.csv',
                'weekday_timetable' : {
                    'workbook' : u'M04_stop_times.xlsx',
                    'sheetname' : u'M04_stop_times（平日）',
                    'stop_offset_row' : 13,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 15,
                    'timetable_offset_col' : 3,
                },
                'saturday_timetable' : {
                    'workbook' : u'M04_stop_times.xlsx',
                    'sheetname' : u'M04_stop_times（土曜）',
                    'stop_offset_row' : 14,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 16,
                    'timetable_offset_col' : 3,
                },
                'holyday_timetable' : {
                }
            }
        ]
    },
    {
        'operation_company' : u'草津市',
        'line_name' : u'笠縫東常盤線',
        'shape' : 'M05_shapes/M05.shp',
        'srid' : 2448 , #JGD2000/平面直角座標系6
        'timetables' : [
            {
                'route' : u'Route5R',
                'bus_stops' : u'M05_stops_cw.csv',
                'weekday_timetable' : {
                    'workbook' : u'M05_stop_times.xlsx',
                    'sheetname' : u'M05_stop_times',
                    'stop_offset_row' : 6,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 7,
                    'timetable_offset_col' : 3,
                },
                'saturday_timetable' : {
                    'workbook' : u'M05_stop_times.xlsx',
                    'sheetname' : u'M05_stop_times',
                    'stop_offset_row' : 6,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 7,
                    'timetable_offset_col' : 3,
                },
                'holyday_timetable' : {
                    'workbook' : u'M05_stop_times.xlsx',
                    'sheetname' : u'M05_stop_times',
                    'stop_offset_row' : 6,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 7,
                    'timetable_offset_col' : 3,
                }
            }
            ,{
                'route' : u'Route5L',
                'bus_stops' : u'M05_stops_cw.csv',
                'weekday_timetable' : {
                    'workbook' : u'M05_stop_times.xlsx',
                    'sheetname' : u'M05_stop_times',
                    'stop_offset_row' : 13,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 14,
                    'timetable_offset_col' : 3,
                },
                'saturday_timetable' : {
                    'workbook' : u'M05_stop_times.xlsx',
                    'sheetname' : u'M05_stop_times',
                    'stop_offset_row' : 13,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 14,
                    'timetable_offset_col' : 3,
                },
                'holyday_timetable' : {
                    'workbook' : u'M05_stop_times.xlsx',
                    'sheetname' : u'M05_stop_times',
                    'stop_offset_row' : 13,
                    'stop_offset_col' : 3,
                    'timetable_offset_row' : 14,
                    'timetable_offset_col' : 3,
                }
            }
        ]
    }
]

def _get_timetable(download_path, tinfo):
    if not 'workbook' in tinfo:
        return []
    workbook_path = os.path.join(download_path, tinfo['workbook'])
    if not os.path.exists(workbook_path):
        raise Exception('Not found.', workbook_path)
    chk_func = None
    if 'check_func' in tinfo:
        chk_func = getattr(callback, tinfo['check_func'])
    timetables = bus_data_parser.get_bus_timetable(
        workbook_path,
        tinfo['sheetname'],
        tinfo['stop_offset_row'],
        tinfo['stop_offset_col'],
        bus_data_parser.DataDirection.col,
        tinfo['timetable_offset_row'],
        tinfo['timetable_offset_col'],
        chk_func
    )
    return timetables

bus_db.setup('bus_stop.sqlite', 'C:\\tool\\spatialite\\mod_spatialite-4.2.0-win-x86\\mod_spatialite.dll')
rule = {
    u'山田小学校前': u'山田小学校',
    u'木ノ川東':u'木川東',
    u'西渋川１丁目': u'西渋川一丁目',
    u'野村八丁目': u'野村８丁目',
    u'新堂中学校前': u'新堂中学校'

}
download_path = 'download'

for s in src:
    timetables = []
    for tbl in s['timetables']:
        bus_stop_path = os.path.join(download_path, tbl['bus_stops'])
        bus_stops = bus_data_parser.get_bus_stop(bus_stop_path)

        bus_data_parser.convert_bus_stop_name(rule, bus_stops)
        timetable = _get_timetable(download_path, tbl['weekday_timetable'])
        saturday_timetable = _get_timetable(download_path, tbl['saturday_timetable'])
        holyday_timetable = _get_timetable(download_path, tbl['holyday_timetable'])
        timetables.append({
            'route' : tbl['route'],
            'bus_stops' : bus_stops,
            'weekday_timetable' : timetable,
            'saturday_timetable' : saturday_timetable,
            'holyday_timetable' : holyday_timetable
        })
    shapepath = os.path.join(download_path, s['shape'])
    bus_db.import_bus(s['operation_company'], s['line_name'], shapepath, s['srid'], timetables)
