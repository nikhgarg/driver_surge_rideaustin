import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from functools import partial
import pytz


def load_data(folder = 'data/rideaustin/', filename = 'rides_24hours.csv'):
    df = pd.read_csv(folder + filename)
    # df = reverse_engineer_total_earnings(df)
    return df

#from https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
from math import radians, cos, sin, asin, sqrt
def haversine(lat1, lon1, lat2, lon2):

      R = 3959.87433 # this is in miles.  For Earth radius in kilometers use 6372.8 km

      dLat = radians(lat2 - lat1)
      dLon = radians(lon2 - lon1)
      lat1 = radians(lat1)
      lat2 = radians(lat2)

      a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
      c = 2*asin(sqrt(a))

      return R * c

def weib(x,n,a):
    return (a / n) * (x / n)**(a - 1) * np.exp(-(x / n)**a)

def argmin(A):
    return np.unravel_index(A.argmin(), A.shape)

tz = pytz.timezone('America/Chicago') #Austin's time zone
epoch = tz.localize(datetime.datetime.utcfromtimestamp(0))
def hours_from_epoch(datime):
    # try:
    total_time =  (datime - epoch).total_seconds()/3600
    return total_time
    # except Exception:
    #     return np.nan

def weighted_mean_variance(df, col, weight_col):
    dfloc = df.dropna(subset = [col, weight_col])
    sum_weights = dfloc[weight_col].sum()
    mean = dfloc.eval('({0}*{1})'.format(col, weight_col)).sum()/sum_weights
    variance = dfloc.eval('(({0}-@mean)**2*{1})/@sum_weights'.format(col, weight_col)).sum()
    return mean, variance

def add_alternative_payments_to_df(df, payment_functions):
    for fun in payment_functions:
        df = fun(df)
    return df
