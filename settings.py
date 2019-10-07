from trip_indifference.matching_functions import *
from payment.payment_functions import *
import copy
import seaborn as sns

match_functions = [get_match_for_row_lastdriverinarea, get_match_for_row_nextdrivermatched]
relevant_columns = ['dispatched_on', 'started_on', 'completed_on','distance_travelled', 'end_location_lat', 'end_location_long','driver_rating', 'rider_rating', 'active_driver_id','requested_car_category', 'surge_factor','start_location_long', 'start_location_lat', 'rider_id','round_up_amount', 'driver_reached_on','base_fare', 'total_fare', 'rate_per_mile', 'rate_per_minute','time_fare', 'driver_accepted_on', 'esimtated_time_arrive', 'tipped_on','tip', 'driving_time_to_rider', 'driving_distance_to_rider','status', 'driver_id','car_categories_bitmask', 'rating', 'cancelled_on','started_on_hours_since_epoch', 'completed_on_hours_since_epoch','dispatched_on_hours_since_epoch', 'start_hour', 'start_hour_rounded','end_hour', 'end_hour_rounded', 'dispatch_hour','dispatch_hour_rounded', 'start_day_rounded', 'ride_total_time','ride_total_time_seconds', 'surged_trip', 'miles']

settings_server_preprocessing = {
    'folder' : 'data/rideaustin/',
    'number_of_processors' : 4,
    'label' : 'ridesfinal',
    'preprocessed_data_filelabel': 'ridesfinal',
    'fileending_with_start_df' : '_validreverseengineered',
    'functions_to_run'   :['pipeline_data_preprocessing'],
}

settings_server_2months = {
    'number_of_processors' : 55,
    'relevant_columns' : relevant_columns,
    'label' : 'ridesfinal',
    'preprocessed_data_filelabel': 'ridesfinal',
    'fileending_with_start_df' : '_validreverseengineered',
    'folder' : 'data/rideaustin/',
    'driver_shift_columns' : ['active_driver_id'],
    'numbers_hours_next' : [1, 1.5],
    'match_functions' : [get_match_for_row_lastdriverinarea_dispatchtime, get_match_for_row_lastdriverinarea, get_match_for_row_nextdrivermatched],
    'functions_to_run'   :['pipeline_data_preprocessing','get_match_driver_index','get_driver_trips_in_period_for_matches','get_earnings_in_period'],
    'payment_functions' : payment_functions_2months,
    'payment_function_names' : payment_function_2months_names,
    'payment_function_mult' : 'pure_mult_bysurgefactor_fare',
    'payment_function_add' : 'pure_addsurge_bysurgefactor_fare'
}

settings_server_3weeks = copy.deepcopy(settings_server_2months)
settings_server_3weeks['fileending_with_start_df'] = '_3weeks'
settings_server_3weeks['payment_functions'] = payment_functions_3weeks
settings_server_3weeks['payment_function_names'] = payment_function_3weeks_names
settings_server_3weeks['payment_function_mult'] = 'pure_mult_bysurgefactor_3weeks_fare'
settings_server_3weeks['payment_function_add'] = 'pure_addsurge_bysurgefactor_3weeks_fare'

settings_server_24hrs = copy.deepcopy(settings_server_2months)
settings_server_24hrs['fileending_with_start_df'] = '_24hours'
settings_server_24hrs['payment_functions'] = payment_functions_24hrs
settings_server_24hrs['payment_function_names'] = payment_function_24hrs_names
settings_server_24hrs['payment_function_mult'] = 'pure_mult_bysurgefactor_24hrs_fare'
settings_server_24hrs['payment_function_add'] = 'pure_addsurge_bysurgefactor_24hrs_fare'

settings_server_10hrs = copy.deepcopy(settings_server_2months)
settings_server_10hrs['fileending_with_start_df'] = '_10hours'
settings_server_10hrs['payment_functions'] = payment_functions_10hrs
settings_server_10hrs['payment_function_names'] = payment_function_10hrs_names
settings_server_10hrs['payment_function_mult'] = 'pure_mult_bysurgefactor_10hrs_fare'
settings_server_10hrs['payment_function_add'] = 'pure_addsurge_bysurgefactor_10hrs_fare'


plotting_differences = {
    'number_of_processors' : 4,
    'outputrunlabel' : 'alldata',
    'numbers_hours_next' : [1],
    'match_functions' : [get_match_for_row_lastdriverinarea_dispatchtime],
    'functions_to_run' : ['plot_drivershift_earnings','plot_drivershift_earnings_variancebyaddmult','plot_tripindifference_histogram','plot_tripindifference_variancebyaddmult','supplementary_facts'],
    'plot_colors' :[sns.light_palette('black', 2, input="xkcd").as_hex()[-1], sns.light_palette((210, 90, 60), 2, input="husl").as_hex()[-1]]
}

settings_plotting_2months = copy.copy(settings_server_2months)
settings_plotting_2months.update(plotting_differences)

settings_plotting_3weeks = copy.copy(settings_server_3weeks)
settings_plotting_3weeks.update(plotting_differences)

settings_plotting_24hrs = copy.copy(settings_server_24hrs)
settings_plotting_24hrs.update(plotting_differences)

settings_plotting_10hrs = copy.copy(settings_server_10hrs)
settings_plotting_10hrs.update(plotting_differences)
