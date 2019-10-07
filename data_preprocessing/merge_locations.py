import sys
sys.path.append('../')

from latexify import *
import pandas as pd
import numpy as np
from pandas_apply_parallel import parallelize_on_rows
from functools import partial

def is_point_in_path(x, y, poly):
    """
    code from https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule

    x, y -- x and y coordinates of point
    poly -- a list of tuples [(x, y), (x, y), ...]
    """
    num = len(poly)
    i = 0
    j = num - 1
    c = False
    for i in range(num):
        if ((poly[i][1] > y) != (poly[j][1] > y)) and \
                (x < poly[i][0] + (poly[j][0] - poly[i][0]) * (y - poly[i][1]) /
                                  (poly[j][1] - poly[i][1])):
            c = not c
        j = i
    return c

def find_polygon_for_longlat(x,y, polygons):
    is_in = polygons['csv_array'].apply(lambda poly: is_point_in_path(x,y,poly))
    return ','.join([str(xx[0]) for xx in enumerate(is_in.tolist()) if xx[1]])

def _find_polygon_for_longlatfromrow(row, polygons, field):
    return find_polygon_for_longlat(row['{}_location_long'.format(field)], row['{}_location_lat'.format(field)], polygons)

def merge_locations(data_file = 'rides_clean.csv', polygons_file = 'polygons_lessoverlap_closed.csv', folder = '../data/rideaustin/', polygons_name = ''):
    df = pd.read_csv(folder + data_file)

    polygons = pd.read_csv(folder + polygons_file)
    polygons['csv_array'] = polygons['csv_array'].apply(eval)

    for field in ['start', 'end']:
        print('now merging {} areas'.format(field))
        funloc = partial(_find_polygon_for_longlatfromrow, polygons = polygons, field = field)
        df['{}_area{}'.format(field,polygons_name)] = parallelize_on_rows(df, funloc)
        # df.apply(lambda x: find_polygon_for_longlat(x['{}_location_long'.format(field)], x['{}_location_lat'.format(field)], polygons), axis = 1)

    df.to_csv(folder + 'rides_clean.csv')

if __name__== "__main__":
    merge_locations()
