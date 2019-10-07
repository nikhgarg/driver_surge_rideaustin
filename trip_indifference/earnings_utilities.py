import pandas as pd
from functools import partial
from generic.pandas_apply_parallel import *

# For the given row, returns sum of same driver's earnings in a given period, prorating earnings for unfinished trips
# Meant to be used in df.apply(fun, axis = 1)
def get_earnings_in_period_prorate_unfinished_trips(drivertrips, payment_function_names, start_time, end_time, start_time_col = 'start_hour'):
    driver_id_trips_started_time_right = drivertrips.query('({0} <= @end_time) and ({0} >= @start_time)'.format(start_time_col))
    completed_trips = driver_id_trips_started_time_right.query('(end_hour <= @end_time)')

    partial_trips = driver_id_trips_started_time_right.query('(end_hour > @end_time)')
    partial_trip_overlap_amount = partial_trips.eval('(@end_time - {0})/(end_hour - {0})'.format(start_time_col))


    earnings = [0 for _ in payment_function_names]
    for en, earnings_field in enumerate(payment_function_names):
        completed_trip_sum = completed_trips[earnings_field].sum(skipna = False) #propagate if any of the driver's trips have invalid columns
        partial_trip_sum = (partial_trip_overlap_amount * partial_trips[earnings_field]).sum(skipna = False) #propagate if any of the driver's trips have invalid columns
        earnings[en] = completed_trip_sum + partial_trip_sum

    return earnings

###################### Code for getting earnings in period in a fixed time period after a certain start time #######################
# For the given row, returns sum of same driver's earnings in a given period **after the start time of this row's trip**, prorating earnings for unfinished trips
# Meant to be used in df.apply(fun, axis = 1)
def get_earnings_in_period_fixed_time_difference_from_row_prorate_unfinished_trips(row, payment_function_names, number_hours_next, df_grouped, start_time_col = 'start_hour'):
    start_time = row[start_time_col]
    end_time = start_time + number_hours_next
    driverid = row.driver_id

    drivertrips = df_grouped.get_group(driverid)

    return get_earnings_in_period_prorate_unfinished_trips(drivertrips, payment_function_names, start_time, end_time)

def get_earnings_in_period_for_match_fixed_time_difference_from_row_prorate_unfinished_trips(row, match_column, payment_function_names, number_hours_next, df_grouped, df, use_matched_row_start_time = False, start_time_col = 'start_hour'):
    if row[match_column] == -1:
        return [np.nan for _ in payment_function_names]
    matched_row = df[df.row_num == row[match_column]]
    if matched_row.shape[0] == 0:
        return [np.nan for _ in payment_function_names]
    matched_row = matched_row.iloc[0,:]

    if use_matched_row_start_time:
        start_time = matched_row[start_time_col]
    else:
        start_time = row[start_time_col]
    end_time = row[start_time_col] + number_hours_next

    driverid = matched_row.driver_id


    drivertrips = df_grouped.get_group(driverid)

    return get_earnings_in_period_prorate_unfinished_trips(drivertrips, payment_function_names, start_time, end_time)
