

# from geopy.distance import distance as distancelatlong
from functools import partial
import numpy as np
import pandas as pd
from generic.pandas_apply_parallel import parallelize_on_rows
from settings import *
from utilities import *
### Get nearest matche for each row, using combination of distance and difference between start times


############################# Distance functions ##########################
#Distance between two rows in miles (default is trip start location)
def get_distance_miles(row1, row2, prefix1 = 'start_location_', prefix2 = 'start_location_'):
    # loc1 = (row1[prefix1 + 'lat'], row1[prefix1 + 'long'])
    # loc2 = (row2[prefix2 + 'lat'], row2[prefix2 + 'long'])
    #distancelatlong(loc1, loc2).miles

    return haversine(row1[prefix1 + 'lat'], row1[prefix1 + 'long'], row2[prefix2 + 'lat'], row2[prefix2 + 'long'])

#Distance between two rows combining time and distance, equating 20 miles to 1 hour
def get_distance_combined(row1, row2, distance_multiplier = 1/20., prefix1 = 'start_location_', prefix2 = 'start_location_', time_field1 = 'start_hour', time_field2 = 'start_hour'):
    distance_miles = get_distance_miles(row1, row2, prefix1 = prefix1, prefix2 = prefix2 )
    distance_time = abs(row1[time_field1] - row2[time_field2])
    return distance_time + distance_miles*distance_multiplier # (time in hours) + (distance in miles)/(20 miles/hour)

############## Get matches functions #####################################
# for the given row, finds the best match in the next **num_after_to_check** rows
def get_match_for_row_nextdrivermatched(row, df, distance_multiplier = 1/20., num_after_to_check = 50):
    if row.row_num == df.shape[0]-1: return (np.nan, np.nan)
    partial_dist = partial(get_distance_combined, row2 = row)
    dists = df.iloc[row.row_num + 1: row.row_num + num_after_to_check + 1, :].apply(partial_dist, axis = 1).tolist()
    argmin = np.argmin(dists)
    return row.row_num + 1 + argmin, dists[argmin]
get_match_for_row_nextdrivermatched.name = 'tripdriver_matched_index'
get_match_for_row_nextdrivermatched.sort_field = 'start_hour'


# for the given row, finds the best match in the previous **num_prev_to_check** rows, based on end_location
# i.e., the last driver who ended a drip nearby
# threshold is the highest "distance" (time + mileage) that can be to be close. Set it at equivalent to half an hour
def get_match_for_row_lastdriverinarea(row, df, distance_multiplier = 1/20., num_prev_to_check = 800, threshold = .7):
    if row.row_num == 0: return (np.nan, np.nan)
    rowstarthour = row.start_hour
    # partial_dist = partial(get_distance_combined, row2 = row, prefix1 = 'end_location_', time_field1 = 'end_hour')
    partial_dist = partial(get_distance_combined, row2 = row, prefix1 = 'end_location_', time_field1 = 'end_hour')

    relevant_rows_before = df.iloc[max(0, row.row_num - num_prev_to_check): row.row_num, :]
    relevant = relevant_rows_before.query('(end_hour < @rowstarthour) and (end_hour > @rowstarthour - @threshold)') #Need to find the last trips that end before this one starts
    # get drivers attached to the remaining relevant ones
        # check that they did NOT start another trip before row.start_hour, except for the trip from that driver that I'm considering, equivalent to getting _last_ trip in relevant for that driver
    relevant = relevant.drop_duplicates(subset = 'driver_id', keep = 'last', inplace =False)

    relevant = relevant[relevant.driver_id != row.driver_id] #check that their driver id is different than the one I want to match

    if relevant.shape[0] == 0:
        return (np.nan, np.nan)

    dists = relevant.apply(partial_dist, axis = 1)

    # apply threshold
    valid = dists < threshold
    relevant = relevant[valid]

    if relevant.shape[0] == 0:
        return (np.nan, np.nan)
    dists = dists[valid].tolist()

    argmin = np.argmin(dists)
    return relevant.iloc[argmin,:].row_num, dists[argmin]

get_match_for_row_lastdriverinarea.name = 'opendriver_matched_index'
get_match_for_row_lastdriverinarea.sort_field = 'start_hour'

def get_match_for_row_lastdriverinarea_dispatchtime(row, df, distance_multiplier = 1/20., num_prev_to_check = 800, threshold = .7):
    if row.row_num == 0: return (np.nan, np.nan)
    rowstarthour = row.dispatch_hour
    # partial_dist = partial(get_distance_combined, row2 = row, prefix1 = 'end_location_', time_field1 = 'end_hour')
    partial_dist = partial(get_distance_combined, row2 = row, prefix1 = 'end_location_', time_field1 = 'end_hour', time_field2 = 'dispatch_hour')

    relevant_rows_before = df.iloc[max(0, row.row_num - num_prev_to_check): row.row_num, :]
    relevant = relevant_rows_before.query('(end_hour < @rowstarthour) and (end_hour > @rowstarthour - @threshold)') #Need to find the last trips that end before this one starts
    # get drivers attached to the remaining relevant ones
        # check that they did NOT start another trip before row.start_hour, except for the trip from that driver that I'm considering, equivalent to getting _last_ trip in relevant for that driver
    relevant = relevant.drop_duplicates(subset = 'driver_id', keep = 'last', inplace =False)

    relevant = relevant[relevant.driver_id != row.driver_id] #check that their driver id is different than the one I want to match

    if relevant.shape[0] == 0:
        return (np.nan, np.nan)

    dists = relevant.apply(partial_dist, axis = 1)

    # apply threshold
    valid = dists < threshold
    relevant = relevant[valid]

    if relevant.shape[0] == 0:
        return (np.nan, np.nan)
    dists = dists[valid].tolist()

    argmin = np.argmin(dists)
    return relevant.iloc[argmin,:].row_num, dists[argmin]

get_match_for_row_lastdriverinarea_dispatchtime.name = 'opendriver_dispatchtime_matched_index'
get_match_for_row_lastdriverinarea_dispatchtime.sort_field = 'dispatch_hour'

# for the given dataframe, finds the best match for each row
def add_matches_and_distancetomatch_to_df(df, match_function = get_match_for_row_nextdrivermatched):
    partial_match_fun = partial(match_function, df = df)
    matches_and_distances =  parallelize_on_rows(df, partial_match_fun) #df.apply(partial_match_fun, axis = 1) #
    df[[match_function.name, match_function.name.replace('index', 'distance')]] = pd.DataFrame(matches_and_distances.values.tolist(), index= matches_and_distances.index)
    return df

#################
def get_match_driver_index(df, match_functions =[get_match_for_row_nextdrivermatched, get_match_for_row_lastdriverinarea], plot_statistics = False):
    df.sort_values (by = 'start_hour', inplace = True) #TODO replaced from start_hour to dispatch_hour
    df['row_num'] = df.index

    for match_function in match_functions:
        print(match_function.name)
        df = add_matches_and_distancetomatch_to_df(df, match_function = match_function)
        if plot_statistics:
            df.eval('{} - row_num'.format(match_function.name)).hist(bins = 20)
            plt.show()
            df[match_function.name.replace('index', 'distance')].hist(bins = np.linspace(0, 1, 50))
            plt.yscale('log')
            plt.show()
        print("Number matched: {}/{}".format(df[~df[match_function.name].isna()].shape[0], df.shape[0]))

    return df
