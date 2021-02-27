from trip_indifference.matching_functions import *
from payment.payment_functions import *
import copy
import seaborn as sns

match_functions = [get_match_for_row_lastdriverinarea, get_match_for_row_nextdrivermatched]
relevant_columns = [
    "dispatched_on",
    "started_on",
    "completed_on",
    "distance_travelled",
    "end_location_lat",
    "end_location_long",
    "driver_rating",
    "rider_rating",
    "active_driver_id",
    "requested_car_category",
    "surge_factor",
    "start_location_long",
    "start_location_lat",
    "rider_id",
    "round_up_amount",
    "driver_reached_on",
    "base_fare",
    "total_fare",
    "rate_per_mile",
    "rate_per_minute",
    "time_fare",
    "driver_accepted_on",
    "esimtated_time_arrive",
    "tipped_on",
    "tip",
    "driving_time_to_rider",
    "driving_distance_to_rider",
    "status",
    "driver_id",
    "car_categories_bitmask",
    "rating",
    "cancelled_on",
    "started_on_hours_since_epoch",
    "completed_on_hours_since_epoch",
    "dispatched_on_hours_since_epoch",
    "start_hour",
    "start_hour_rounded",
    "end_hour",
    "end_hour_rounded",
    "dispatch_hour",
    "dispatch_hour_rounded",
    "start_day_rounded",
    "ride_total_time",
    "ride_total_time_seconds",
    "surged_trip",
    "miles",
]

settings_datapreprocessing = {"relevant_columns": relevant_columns, "filelabel": "rides3", "folder": "data/rideaustin/"}

settings_server_2months = {
    "number_of_processors": 55,
    "relevant_columns": relevant_columns,
    "label": "rideswithaddmin_disptime",
    "preprocessed_data_filelabel": "ridesfinal",
    "fileending_with_start_df": "_validreverseengineered",
    "folder": "data/rideaustin/",
    "driver_shift_columns": ["active_driver_id"],
    "numbers_hours_next": [1, 1.5, 2],  # [1, 1.5, 2],
    "match_functions": [
        get_match_for_row_lastdriverinarea_dispatchtime,
        get_match_for_row_lastdriverinarea,
        get_match_for_row_nextdrivermatched,
    ],
    "functions_to_run": [
        "pipeline_data_preprocessing",
        "match_trips",
        "get_match_driver_index",
        "get_driver_trips_in_period_for_matches",
        "get_earnings_in_period",
    ],
    "payment_functions": payment_functions_2months_withmin,
    "payment_function_names": payment_function_2months_withmin_names,
    "payment_function_mult": "pure_mult_bysurgefactor_fare",
    "payment_function_add": "pure_addsurge_bysurgefactor_fare",
}

settings_server_2months_fakefactor = copy.deepcopy(settings_server_2months)
settings_server_2months_fakefactor["label"] = "ridesfakefactor"
settings_server_2months_fakefactor["preprocessed_data_filelabel"] = "ridesfakefactor"
settings_server_2months_fakefactor["payment_functions"] = payment_functions_2months_withmin_fakefactor
settings_server_2months_fakefactor["payment_function_names"] = payment_function_2months_withmin_names_fakefactor


settings_server_3weeks = copy.deepcopy(settings_server_2months)
settings_server_3weeks["fileending_with_start_df"] = "_3weeks"
settings_server_3weeks["payment_functions"] = payment_functions_3weeks
settings_server_3weeks["payment_function_names"] = payment_function_3weeks_names
settings_server_3weeks["payment_function_mult"] = "pure_mult_bysurgefactor_3weeks_fare"
settings_server_3weeks["payment_function_add"] = "pure_addsurge_bysurgefactor_3weeks_fare"

settings_server_24hrs = copy.deepcopy(settings_server_2months)
settings_server_24hrs["fileending_with_start_df"] = "_24hours"
settings_server_24hrs["payment_functions"] = payment_functions_24hrs
settings_server_24hrs["payment_function_names"] = payment_function_24hrs_names
settings_server_24hrs["payment_function_mult"] = "pure_mult_bysurgefactor_24hrs_fare"
settings_server_24hrs["payment_function_add"] = "pure_addsurge_bysurgefactor_24hrs_fare"

settings_server_10hrs = copy.deepcopy(settings_server_2months)
settings_server_10hrs["fileending_with_start_df"] = "_10hours"
settings_server_10hrs["payment_functions"] = payment_functions_10hrs
settings_server_10hrs["payment_function_names"] = payment_function_10hrs_names
settings_server_10hrs["payment_function_mult"] = "pure_mult_bysurgefactor_10hrs_fare"
settings_server_10hrs["payment_function_add"] = "pure_addsurge_bysurgefactor_10hrs_fare"


plotting_differences = {
    "outputrunlabel": "alldata2paymentfuns",
    "numbers_hours_next": [1, 1.5, 2],  # [1, 1.5, 2],#[.75, 1, 1.25, 1.5],#, 1.25, 1.5],
    "match_functions": [
        get_match_for_row_lastdriverinarea_dispatchtime,
        get_match_for_row_nextdrivermatched,
    ],
    "functions_to_run": [
        "plot_tripindifference_histogram",
        "plot_drivershift_earnings",
        "supplementary_facts",
        "plot_tripindifference_variancebyaddmult",
    ],
    "plot_colors": [
        sns.light_palette("black", 2, input="xkcd").as_hex()[-1],
        sns.light_palette((210, 90, 60), 2, input="husl").as_hex()[-1],
    ],
    # "payment_functions": payment_functions_2months_withmin,
    # "payment_function_names": payment_function_2months_withmin_names,
    "skip_mimicfare_in_plot_stuff": False,
}

settings_plotting_puresurgeonly = copy.copy(settings_server_2months)
settings_plotting_puresurgeonly.update(plotting_differences)
settings_plotting_puresurgeonly["outputrunlabel"] = "pureonly"
settings_plotting_puresurgeonly["payment_functions"] = payment_functions_2months_pureonly
settings_plotting_puresurgeonly["payment_function_names"] = payment_function_2months_pureonly_names
settings_plotting_puresurgeonly["numbers_hours_next"] = [1.5]

settings_plotting_fakefactor = copy.copy(settings_server_2months_fakefactor)
settings_plotting_fakefactor.update(plotting_differences)
settings_plotting_fakefactor["outputrunlabel"] = "fakedata"
settings_plotting_fakefactor["payment_functions"] = payment_functions_2months_withmin_fakefactor
settings_plotting_fakefactor["payment_function_names"] = payment_function_2months_withmin_names_fakefactor
settings_plotting_fakefactor["ylim"] = (-60, 40)

settings_plotting_2months_supplement = copy.copy(settings_server_2months)
settings_plotting_2months_supplement.update(plotting_differences)
settings_plotting_2months_supplement["functions_to_run"] = ["supplementary_facts"]

settings_plotting_2months = copy.copy(settings_server_2months)
settings_plotting_2months.update(plotting_differences)

settings_plotting_3weeks = copy.copy(settings_server_3weeks)
settings_plotting_3weeks.update(plotting_differences)

settings_plotting_24hrs = copy.copy(settings_server_24hrs)
settings_plotting_24hrs.update(plotting_differences)

settings_plotting_10hrs = copy.copy(settings_server_10hrs)
settings_plotting_10hrs.update(plotting_differences)


settings_all_withdispatchhour = {
    "override_start_with_dispatch": True,
    "number_of_processors": 55,
    "relevant_columns": relevant_columns,
    "preprocessed_data_filelabel": "rides_usedispatch",
    "label": "rides_usedispatch",
    "fileending_with_start_df": "_validreverseengineered",
    "folder": "data/rideaustin/",
    "numbers_hours_next": [1.5],  # [1, 1.5, 2],
    "match_functions": [
        get_match_for_row_lastdriverinarea_dispatchtime,
        get_match_for_row_nextdrivermatched,
    ],
    "functions_to_run": [
        "match_trips",
        "get_match_driver_index",
        "get_driver_trips_in_period_for_matches",
        "get_earnings_in_period",
    ],  #'match_trips', 'get_match_driver_index', 'get_driver_trips_in_period_for_matches',
    "payment_functions": payment_functions_2months,
    "payment_function_names": payment_function_2months_names,
    "payment_function_mult": "pure_mult_bysurgefactor_fare",
    "payment_function_add": "pure_addsurge_bysurgefactor_fare",
}

settings_all_dispatchstartmeasurement = {
    "number_of_processors": 55,
    "relevant_columns": relevant_columns,
    "outputrunlabel": "rideswithaddmin_dispstartmeasurement",
    "label": "rideswithaddmin_disptime",
    "fileending_with_start_df": "_validreverseengineered",
    "folder": "data/rideaustin/",
    "numbers_hours_next": [1.5],  # [1, 1.5, 2],
    "earnings_period_start_time": "dispatch_hour",
    "match_functions": [get_match_for_row_lastdriverinarea_dispatchtime],
    "functions_to_run": ["get_earnings_in_period"],
    "payment_functions": payment_functions_2months,
    "payment_function_names": payment_function_2months_names,
    "payment_function_mult": "pure_mult_bysurgefactor_fare",
    "payment_function_add": "pure_addsurge_bysurgefactor_fare",
}

settings_plotting_dispatchhour = copy.copy(settings_all_withdispatchhour)
settings_plotting_dispatchhour.update(plotting_differences)
settings_plotting_dispatchhour["outputrunlabel"] = "dispatchhour"
settings_plotting_dispatchhour["ylim"] = (-60, 40)
settings_plotting_dispatchstartmeasurement = copy.copy(settings_all_dispatchstartmeasurement)
settings_plotting_dispatchstartmeasurement.update(plotting_differences)
settings_plotting_dispatchstartmeasurement["outputrunlabel"] = "dispstartmeasurement"
settings_plotting_dispatchstartmeasurement["label"] = "rideswithaddmin_disptimestartmeasurement"
settings_plotting_dispatchstartmeasurement["ylim"] = (-20, 50)
