import sys
sys.path.append('../')

from latexify import *
import pandas as pd
import numpy as np

def plot_polygon(ar):
    x = [a[0] for a in ar]
    y = [a[1] for a in ar]

    if max(x) > -96: #completely different area
        return
    plt.plot(x, y, alpha=1,linewidth=2, solid_capstyle='round', zorder=2)

def plot_polygons(coordinate_array, name = 'polygon_map'):
    for poly in coordinate_array:
        plot_polygon(poly)
    saveimage(name, folder = '../plots/')

def close_polygon(coordinates):
    first = coordinates[0]
    last = coordinates[-1]
    if first[0]!= last[0] or first[1]!= last[1]:
        coordinates.append(first)
    return coordinates

def csv_geom_to_array(s):
    s = s.split(' ')
    s = [x.split(',') for x in s]
    s = [[x.replace('b', '').replace("'",'') for x in xx] for xx in s]
    s = [[float(x) if len(x)>0 else np.nan for x in xx] for xx in s]
    s = [x for x in s if (len(x)>0 and ~np.isnan(x[0]))]

    return s

def create_clean_polygons_file(folder, filename):
    polygons = pd.read_csv(folder +  filename)
    polygons['csv_array'] = polygons['csv_geometry'].apply(csv_geom_to_array)
    polygons['csv_array'] = polygons['csv_array'].apply(close_polygon)
    polygons_relevant = polygons.iloc[0:58,:]

    polygons.drop(columns = ['Unnamed: 0'])


    plot_polygons(polygons.csv_array.tolist(), name = 'polygon_map_closed')
    plot_polygons(polygons_relevant.csv_array.tolist(), name = 'polygon_map_closed_lessoverlap')

    polygons.to_csv(folder + 'polygons_closed.csv', index = False)
    polygons_relevant.to_csv(folder + 'polygons_lessoverlap_closed.csv', index = False)


if __name__== "__main__":
    folder = '../data/rideaustin/'
    filename = 'polygons.csv'
    create_clean_polygons_file(folder, filename)
