import pandas as pd
from functools import partial
from generic.pandas_apply_parallel import *
from trip_indifference.earnings_utilities import *

#How this is structured:
    # in the matched df, include lists of trips that are in the period, both own trips and the matched driver's trips
            # added by calling add_trips_in_period_fixed_time_difference_from_row

    # Can run the payment functions (or any other function) on the matched trips

# Returns trips completed by driver who did trip in matched column in next period.
# Will be used for both getting the trip driver's next trips, as well as the matched driver's next trips
def add_trips_in_period_fixed_time_difference_from_row(row, number_hours_next, df, df_grouped,match_column = 'row_num', start_time_col = 'start_hour'):
    if row[match_column] == -1:
        return None

    matched_row = df[df.row_num == row[match_column]]

    if matched_row.shape[0] == 0:
        return None

    matched_row = matched_row.iloc[0,:]

    start_time = row[start_time_col]
    end_time = row[start_time_col] + number_hours_next

    driverid = matched_row.driver_id

    drivertrips = df_grouped.get_group(driverid)

    driver_id_trips_started_time_right = drivertrips.query('({0} < @end_time) and ({0} >= @start_time)'.format(start_time_col))['row_num'].tolist()
    return driver_id_trips_started_time_right

def get_period_earnings_withmatchlists(row, df, trips_list_column, payment_function_names,number_hours_next, start_time_col = 'start_hour'):
    trips = row[trips_list_column]
    if not isinstance(trips, list):
        return [np.nan for _ in range(len(payment_function_names))]

    start_time = row[start_time_col]
    end_time = row[start_time_col] + number_hours_next
    triprows = df.loc[trips, :]
    return get_earnings_in_period_prorate_unfinished_trips(triprows, payment_function_names, start_time, end_time, start_time_col = start_time_col)
