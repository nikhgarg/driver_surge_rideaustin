import pandas as pd
import numpy as np
from functools import partial

rev_eng_mult = 1.01
rev_eng_add = 2.022

def reverse_engineer_withparams(dfloc, multiplier, additive, col_name = 'reverse_engineer_fare'):
    dfloc.loc[:,col_name] = dfloc.eval('rate_per_mile*miles + ride_total_time_seconds/60*rate_per_minute + base_fare')
    dfloc.loc[dfloc.requested_car_category == "b'REGULAR'",'min_fare_for_vehicle_type'] = 4
    dfloc.loc[dfloc.requested_car_category != "b'REGULAR'",'min_fare_for_vehicle_type'] = 10

    dfloc.loc[:,col_name] = dfloc[[col_name, 'min_fare_for_vehicle_type']].values.max(1)
    dfloc.loc[:,col_name] = dfloc.eval('{0}*surge_factor*@multiplier + @additive'.format(col_name))

    return dfloc

def pure_multiplicative_withparams(dfloc, multiplier_to_match_reverse, col_name = 'pure_multiplicative_fare'):
    dfloc.loc[:,col_name] = dfloc.eval('(rate_per_mile*miles + ride_total_time_seconds/60*rate_per_minute)*surge_factor*@multiplier_to_match_reverse')
    return dfloc

def pure_additive_withparams(dfloc, additive, col_name = 'pure_additive_surge_fare', multiplier_to_match_reverse = 1.378218618221581):
    dfloc.loc[:,col_name] = dfloc.eval('(rate_per_mile*miles + ride_total_time_seconds/60*rate_per_minute)*@multiplier_to_match_reverse + (surge_factor-1)*@additive')
    return dfloc

def withmin_additive_surge_withparams(dfloc, additive, col_name = 'withmin_additive_surge_fare', multiplier = rev_eng_mult):
    dfloc.loc[:,col_name] = dfloc.eval('rate_per_mile*miles + ride_total_time_seconds/60*rate_per_minute + base_fare')
    dfloc.loc[dfloc.requested_car_category == "b'REGULAR'",'min_fare_for_vehicle_type'] = 4
    dfloc.loc[dfloc.requested_car_category != "b'REGULAR'",'min_fare_for_vehicle_type'] = 10

    dfloc.loc[:,col_name] = dfloc[[col_name, 'min_fare_for_vehicle_type']].values.max(1)
    dfloc.loc[:,col_name] = dfloc.eval('{0}*@multiplier + (surge_factor-1)*@additive'.format(col_name))

    return dfloc

#multipliers_by_surge is a dictionary
def pure_multiplicative_bysurgefactor_withparams(dfloc, multipliers_by_surge, col_name = 'pure_mult_bysurgefactor_fare'):
    dfloc.loc[:, 'surgefactor_multiplier'] = dfloc.surge_factor.map(multipliers_by_surge)
    dfloc.loc[:,col_name] = dfloc.eval('(rate_per_mile*miles + ride_total_time_seconds/60*rate_per_minute)*surge_factor*surgefactor_multiplier')
    return dfloc

def pure_additive_bysurgefactor_withparams(dfloc, additives_by_surge, multipliers_by_surge, col_name = 'pure_addsurge_bysurgefactor_fare'):
    dfloc.loc[:, 'surgefactor_multiplier'] = dfloc.surge_factor.map(multipliers_by_surge)
    dfloc.loc[:, 'surgefactor_additive'] = dfloc.surge_factor.map(additives_by_surge)

    dfloc.loc[:,col_name] = dfloc.eval('(rate_per_mile*miles + ride_total_time_seconds/60*rate_per_minute)*surgefactor_multiplier + (surge_factor-1)*surgefactor_additive')

    return dfloc

def withmin_additive_bysurgefactor_withparams(dfloc, additives_by_surge, multiplier=rev_eng_mult, col_name = 'withmin_addsurge_bysurgefactor_fare'):

    dfloc.loc[dfloc.requested_car_category == "b'REGULAR'",'min_fare_for_vehicle_type'] = 4
    dfloc.loc[dfloc.requested_car_category != "b'REGULAR'",'min_fare_for_vehicle_type'] = 10
    dfloc.loc[:, 'surgefactor_additive'] = dfloc.surge_factor.map(additives_by_surge)

    dfloc.loc[:,col_name] = dfloc.eval('rate_per_mile*miles + ride_total_time_seconds/60*rate_per_minute + base_fare')
    dfloc.loc[:,col_name] = dfloc[[col_name, 'min_fare_for_vehicle_type']].values.max(1)

    dfloc.loc[:,col_name] = dfloc.eval('{0}*@multiplier + (surge_factor-1)*surgefactor_additive'.format(col_name))

    return dfloc

# def constant_payment_per_trip_withparams(dfloc, col_name = 'constant_fare', constant = 20):
#     dfloc.loc[:,col_name] =
#     return dfloc
