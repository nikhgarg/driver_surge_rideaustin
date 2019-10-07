import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from utilities import *
import pytz

# data split columnwise over 2 files
# I adapt pre-processing code from https://github.com/estherjsuh/RideAustin/blob/master/RideAustinDataProject.ipynb
# Data notes:
    # dispatch_location_lat is incorrect -- column is just a copy of dispatch_location_long
    # There are many trips with incorrect distances, lengths; these are replaced by nan.
    # Don't drop trips, instead replace with nan in appropriate place so that they propagate in the session calculations

def clean_and_merge_datafiles(folder = 'data/rideaustin/', filelabel = 'rides'):
    filename1 = 'Rides_DataA.csv'
    filename2 = 'Rides_DataB.csv'

    df = pd.read_csv(folder + filename1)
    df2 = pd.read_csv(folder + filename2)

    austin= pd.merge(left= df, right= df2, on='RIDE_ID').set_index('RIDE_ID')
    print('Starting with {} rides'.format(austin.shape[0]))

    # print('Retaining just 10000 trips for testing purposes')
    # austin = austin.iloc[-10000:,] #for testing purposes

    #convert datefields to python date-times, convert to hours since beginning of dataset
    # date_fields = ['driver_reached_on', 'started_on', 'completed_on', 'created_date', 'updated_date', 'driver_accepted_on', 'dispatched_on','cancelled_on']
    date_fields_to_convert = ['started_on', 'completed_on', 'dispatched_on']
    date_fields_newnames = ['start_hour', 'end_hour', 'dispatch_hour']

    for field in date_fields_to_convert:
        print('Converting: {}'.format(field))
        # print(austin[field].head())
        austin.loc[:,field] = pd.to_datetime(austin[field], format= '%Y-%m-%d %H:%M:%S')

        if field == 'dispatched_on': #doesn't have timezone in raw data, but is in UTC time
            austin.loc[:,field] =austin[field].apply(pytz.timezone('UTC').localize)

        austin.loc[:,field] =austin[field].apply(lambda x: x.astimezone(pytz.timezone('America/Chicago'))) #convert all time zones to Central time

        austin.loc[:,'{}_hours_since_epoch'.format(field)] = austin[field].apply(hours_from_epoch)
        # print(austin['{}_hours_since_epoch'.format(field)].tail())



    minhours = min(austin.started_on_hours_since_epoch)

    for en, field in enumerate(date_fields_to_convert):
        austin.loc[:,date_fields_newnames[en]] = austin['{}_hours_since_epoch'.format(field)] - minhours
        austin.loc[:,date_fields_newnames[en] + '_rounded'] = austin[date_fields_newnames[en]].apply(np.floor)

    austin['start_day_rounded'] = (austin.start_hour/24).apply(np.floor)

    # add ride time column
    austin['ride_total_time'] = austin['end_hour'] - austin['start_hour']
    austin['ride_total_time_seconds'] = austin.ride_total_time*3600  #.apply(lambda x: x.total_seconds())

    #add bool for whether was a surge trip
    austin['surged_trip'] = austin.surge_factor>1

    # Dropping incomplete rides (only 2 rides in dataset)
    incomplete =  austin[austin.total_fare.isnull()].index
    austin.loc[incomplete, 'total_fare'] = np.nan
    print('Replaced {} trips with total fare null'.format(len(incomplete)))

    # add miles column
    austin['miles']= austin['distance_travelled']*.000621371

    # drop data where there are too many/few miles or too much/little time
    miles_indices_to_drop = austin[(austin.miles > 100) | (austin.miles <= .25)].index
    austin.loc[miles_indices_to_drop, 'miles'] = np.nan
    # austin.drop(miles_indices_to_drop, inplace = True)

    times_indices_to_drop = austin[(austin.ride_total_time_seconds > 3600) | (austin.ride_total_time_seconds <= 30)].index
    austin.loc[times_indices_to_drop, 'ride_total_time_seconds'] = np.nan

    # austin.drop(times_indices_to_drop, inplace = True)
    print('Replaced {} trips of inappropriate time, {} of distance with nan'.format(len(times_indices_to_drop), len(miles_indices_to_drop)))

    #payment rates
    rates_to_low = austin[(austin.rate_per_minute <=0)].index
    austin.loc[rates_to_low, 'rate_per_minute'] = np.nan
    print('Replaced {} trips with per minute rates too low with nan'.format(len(rates_to_low)))

    rates_to_low = austin[(austin.rate_per_mile <=0)].index
    austin.loc[rates_to_low, 'rate_per_mile'] = np.nan
    print('Replaced {} trips with per mile rates too low with nan'.format(len(rates_to_low)))
    # austin.drop(rates_to_low, inplace = True)

    # Drop trips with 0 surge factor
    surge0 = austin[(austin.surge_factor <=0)].index
    austin.loc[surge0, 'surge_factor'] = np.nan
    # austin.drop(surge0, inplace = True)
    print('Replaced {} trips with 0 surge factor with nan'.format(len(surge0)))

    #Trips that have impossibly high total fare (compared to my reverse engineered fare)
    toohightotalfare = austin[austin.total_fare>480].index
    austin.loc[toohightotalfare, 'total_fare'] = np.nan
    print('Replaced {} trips with too high total_fare with nan'.format(len(toohightotalfare)))


    print('Ended processing with {} trips. Saving file now.'.format(austin.shape[0]))

    austin.to_csv(folder  + filelabel + '.csv', index = False)
    return austin

def create_smaller_files(df = None, folder = '../data/rideaustin/', filelabel = 'rides3', relevant_columns = None):
    print("Creating smaller files")
    if df is None:
        df = pd.read_csv(folder + filelabel + '.csv')
    if relevant_columns is not None:
        df = df[relevant_columns]
    df.query('(started_on_hours_since_epoch<414393) & (413127<started_on_hours_since_epoch)').to_csv(folder + filelabel + '_validreverseengineered.csv', index = False)
    df[(df.start_hour>=6630) & (df.start_hour<=7134)].to_csv(folder + filelabel + '_3weeks.csv', index = False)
    df[(df.start_hour>=6870) & (df.start_hour<=6894)].to_csv(folder + filelabel + '_24hours.csv', index = False)
    df[(df.start_hour>=6880) & (df.start_hour<=6890)].to_csv(folder + filelabel + '_10hours.csv', index = False)

if __name__== "__main__":
    folder = '../data/rideaustin/'
    clean_and_merge_datafiles(folder)
