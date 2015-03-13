# -*- coding: utf-8 -*-
import bus_data_parser
import bus_db
import os


def _get_timetable(download_path, tinfo, callback):
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

def import_bus(download_path, src, rule, callback):
    for s in src:
        timetables = []
        for tbl in s['timetables']:
            bus_stop_path = os.path.join(download_path, tbl['bus_stops'])
            bus_stops = bus_data_parser.get_bus_stop(bus_stop_path)

            bus_data_parser.convert_bus_stop_name(rule, bus_stops)
            timetable = _get_timetable(download_path, tbl['weekday_timetable'], callback)
            saturday_timetable = _get_timetable(download_path, tbl['saturday_timetable'], callback)
            holyday_timetable = _get_timetable(download_path, tbl['holyday_timetable'], callback)
            timetables.append({
                'route' : tbl['route'],
                'routeName' : tbl['routeName'],
                'bus_stops' : bus_stops,
                'weekday_timetable' : timetable,
                'saturday_timetable' : saturday_timetable,
                'holyday_timetable' : holyday_timetable
            })
        shapepath = os.path.join(download_path, s['shape'])
        bus_db.import_bus(s['operation_company'], s['line_name'], shapepath, s['srid'], timetables)
