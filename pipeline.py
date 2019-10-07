import pandas as pd
from scipy import stats as stats
import numpy as np
from functools import partial
import copy
import seaborn as sns

from generic.latexify import *
from generic.pandas_apply_parallel import *

from settings import *
from utilities import *

from trip_indifference.matching_period_functions import *
from trip_indifference.matching_functions import *
from trip_indifference.visualization import *
from payment.payment_functions import *
from visualization.visualization_utilities import *
from data_preprocessing import create_clean_rides_file
from shift_earnings.shift_earning_functions import *
from supplementary.supplementary_pipeline import *

def pipeline_data_preprocessing(folder, runlabel):
    df = create_clean_rides_file.clean_and_merge_datafiles(folder, runlabel)
    create_clean_rides_file.create_smaller_files(folder = folder, filelabel = runlabel)

def pipeline(settings):
    folder = settings['folder']
    functions_to_run = settings['functions_to_run']
    runlabel = settings['label'] + settings['fileending_with_start_df']
    outputrunlabel = settings.get('outputrunlabel', runlabel)
    set_number_of_processors(settings.get('number_of_processors', 4))
    skip_mimicfare_in_plot_stuff = settings.get('skip_mimicfare_in_plot_stuff', True)

    numbers_hours_next = settings.get('numbers_hours_next', [])
    match_functions = settings.get('match_functions', [])
    match_functions_names_local = ['row_num']
    match_functions_names_local.extend([x.name for x in match_functions])
    match_functions_names_local = list(reversed(match_functions_names_local))
    payment_function_names = settings.get('payment_function_names', [])

    if skip_mimicfare_in_plot_stuff:
        payment_function_names_plotting = [x for x in payment_function_names if 'mimic' not in x]

    print('Starting pipeline with {}'.format(settings))

    if 'pipeline_data_preprocessing' in functions_to_run:
        print('Starting pipeline_data_preprocessing')
        pipeline_data_preprocessing(folder, settings['preprocessed_data_filelabel'])

    if 'plot_drivershift_earnings' in functions_to_run:
        df = load_data(folder = folder, filename = "{}{}.csv".format(settings['preprocessed_data_filelabel'],settings['fileending_with_start_df']))
        df = add_alternative_payments_to_df(df, settings['payment_functions'])
        for shift_column in settings['driver_shift_columns']:
            print(shift_column)
            df_session = get_session_earnings_df(df, payment_function_names_plotting, shift_column = shift_column)
            print_weighted_mean_variance_session_earnings(df_session, payment_function_names_plotting)
            plot_weighted_histogram_session_earnings(df_session, payment_function_names_plotting, plt_label = outputrunlabel, save_fig = True, colors = settings.get('plot_colors', None))

    if 'plot_drivershift_earnings_variancebyaddmult' in functions_to_run:
        df = load_data(folder = folder, filename = "{}{}.csv".format(settings['preprocessed_data_filelabel'],settings['fileending_with_start_df']))
        df = add_alternative_payments_to_df(df, settings['payment_functions'])
        for shift_column in settings['driver_shift_columns']:
            print(shift_column)
            df_session = get_session_earnings_df(df, payment_function_names, shift_column = shift_column)
            plot_weighted_variance_session_earnings_by_addmult_interpolation(df_session, settings['payment_function_add'], settings['payment_function_mult'], plt_label = outputrunlabel, save_fig = True)

    if 'get_match_driver_index' in functions_to_run:
        print('Starting get_match_driver_index')
        df = load_data(folder = folder, filename = "{}{}.csv".format(settings['preprocessed_data_filelabel'],settings['fileending_with_start_df']))
        df = get_match_driver_index(df, plot_statistics = False, match_functions = settings['match_functions'])
        df.to_csv('{}{}_withmatches.csv'.format(folder, runlabel), index = False)

    if 'get_driver_trips_in_period_for_matches' in functions_to_run:
        print("Starting get_driver_trips_in_period_for_matches")
        df = pd.read_csv('{}{}_withmatches.csv'.format(folder, runlabel))
        df_grouped = df.groupby('driver_id')

        for number_hours_next in numbers_hours_next:
            for match_function_name in match_functions_names_local:
                print(match_function_name, number_hours_next)
                par = partial(add_trips_in_period_fixed_time_difference_from_row,  number_hours_next = number_hours_next, df_grouped = df_grouped, df = df,match_column = match_function_name, start_time_col= 'start_hour')

                df.loc[:,'{}_tripsinperiod_{}'.format(match_function_name.replace('_matched_index', ''), number_hours_next)] = parallelize_on_rows(df, par)

        df.to_csv('{}{}_withtripsinperiod.csv'.format(folder, runlabel), index = False)

    if 'get_earnings_in_period' in functions_to_run:
        print("Starting get_earnings_in_period")
        df = pd.read_csv('{}{}_withtripsinperiod.csv'.format(folder, runlabel))
        df = df.set_index(keys = 'row_num')

        df = add_alternative_payments_to_df(df, settings['payment_functions'])

        for number_hours_next in numbers_hours_next:
            for match_function_name in match_functions_names_local:
                print(number_hours_next, match_function_name)
                trips_list_column = '{}_tripsinperiod_{}'.format(match_function_name.replace('_matched_index', ''), number_hours_next)
                df.loc[:,trips_list_column] = df[trips_list_column].apply(lambda x: eval(x) if isinstance(x, str) else np.nan) #convert string of list into actual list
                # tripslistNOTisnan = ~df[trips_list_column].isna()
                # print(tripslistNOTisnan.sum(), tripslistNOTisnan.count())

                aggstrings = ['{}_{}_earnings{}'.format(match_function_name.replace('_matched_index', ''), func_name, number_hours_next) for func_name in payment_function_names]

                par = partial(get_period_earnings_withmatchlists, df = df, trips_list_column = trips_list_column, payment_function_names = payment_function_names, number_hours_next = number_hours_next, start_time_col= 'start_hour')

                df[aggstrings] = pd.DataFrame(parallelize_on_rows(df, par).tolist())

        df.to_csv('{}{}_with_basicearnings_inperiod.csv'.format(folder, runlabel), index = True)

    if 'plot_tripindifference_histogram' in functions_to_run:
        print("Starting plot_tripindifference_histogram")
        df =  pd.read_csv('{}{}_with_basicearnings_inperiod.csv'.format(folder, runlabel))

        for number_hours_next in numbers_hours_next:
            for match_function in match_functions:
                print(number_hours_next, match_function.name)

                plot_trip_indifference_splitbysurge_length(df, payment_function_names_plotting, number_hours_next, match_function, limit_to_matched_drivers_who_had_trip = True, func_filesave_names = func_filesave_names, plt_label = outputrunlabel, save_fig = True, distance_threshold = 1, start_time_col= 'start_hour', filter_by_dispatch = False)

                plot_trip_indifference(df, payment_function_names_plotting, number_hours_next, match_function, limit_to_matched_drivers_who_had_trip = True, bins = range(-130, 155, 10), func_filesave_names = func_filesave_names, func_pretty_names = func_pretty_names, plt_label = outputrunlabel, save_fig = True, distance_threshold = 1, colors = settings.get('plot_colors', None))

    if 'plot_tripindifference_variancebyaddmult' in functions_to_run:
        print("Starting plot_tripindifference_variancebyaddmult")
        df =  pd.read_csv('{}{}_with_basicearnings_inperiod.csv'.format(folder, runlabel))

        for number_hours_next in numbers_hours_next:
            for match_function in match_functions:
                print(number_hours_next, match_function.name)
                plot_trip_indifference_variance_by_addmult_interpolation(df, settings['payment_function_add'], settings['payment_function_mult'], number_hours_next, match_function, limit_to_matched_drivers_who_had_trip = True, func_filesave_names = func_filesave_names, func_pretty_names = func_pretty_names, plt_label = outputrunlabel, save_fig = True, distance_threshold = 1)

    if 'supplementary_facts' in functions_to_run:
        df =  pd.read_csv('{}{}_with_basicearnings_inperiod.csv'.format(folder, runlabel))
        supplementary_pipeline(outputrunlabel, df, match_functions)




if __name__== "__main__":
    for settings in [settings_server_2months]:
        pipeline(settings)
