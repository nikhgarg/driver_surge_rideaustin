import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

from utilities import *
from generic.latexify import *
from payment.payment_functions import *

def plot_trip_indifference(df, payment_function_names, number_hours_next, match_column, limit_to_matched_drivers_who_had_trip = True, bins = range(-70, 70, 5), func_filesave_names = func_filesave_names, func_pretty_names = func_pretty_names, plt_label = '', save_fig = False, distance_threshold = 1, colors = None):
    dffun = df[df[match_column.name.replace('index', 'distance')] < distance_threshold]
    for en,func in enumerate(payment_function_names):
        evalstr2 = '{}_{}_earnings{}'.format(match_column.name.replace('_matched_index', ''), func, number_hours_next)
        evalstr1 = '{}_{}_earnings{}'.format('row_num', func, number_hours_next)

        if limit_to_matched_drivers_who_had_trip:
            dfloc = dffun[dffun[evalstr2]>0]
            differences = dfloc[evalstr1] - dfloc[evalstr2]
            # return dfloc[differences == 0]

        else:
            differences = dffun[evalstr1] - dffun[evalstr2]
        differences = differences.dropna()
        if colors is None:
            differences.hist(cumulative = False, bins = bins, label = func_pretty_names.get(func, func), alpha = .3)
        else:
            differences.hist(cumulative = False, bins = bins, label = func_pretty_names.get(func, func), alpha = .3, color = colors[en])

        print('{}: {:.5}, {:.5}'.format(func, differences.mean(), differences.var()))
        print('upside down trips: ', (differences<0).sum())

    plt.xlabel('Earnings difference', fontsize = 20)
    plt.ylabel('Number of trips', fontsize = 20)
    plt.yscale('log')

    plt.legend(frameon = False, bbox_to_anchor=(0., 1.02, 1., .0102), loc='lower left', ncol=2, mode="expand", borderaxespad=0., fontsize = 16)
    if save_fig:
        label = 'tripindifference_{}_{}{}_{}_{}{}'.format(plt_label, match_column.name, number_hours_next, ''.join([func_filesave_names.get(func, func) for func in payment_function_names]), str(limit_to_matched_drivers_who_had_trip), distance_threshold)
        saveimage(label, extension = 'png')
    # plt.show()

def plot_trip_indifference_splitbysurge_length(df, payment_function_names, number_hours_next, match_column, limit_to_matched_drivers_who_had_trip = True, bins = range(-70, 70, 5), func_filesave_names = func_filesave_names, func_pretty_names = func_pretty_names, plt_label = '', save_fig = False, distance_threshold = 1, colors = None, timelocname = 'Trip time in seconds', start_time_col= 'dispatch_hour', filter_by_dispatch = False):

    dffun = df[df[match_column.name.replace('index', 'distance')] < distance_threshold]
    timelocname = 'Trip time in seconds'

    # dfloc = dffun
    dfloc = dffun[~dffun.mimic_fare.isna()]

    lencol = 'timecountingrealstarttime'

    if filter_by_dispatch:
        longdispatch = (dfloc.eval('(start_hour - dispatch_hour)*60')>7)
        dfloc = dfloc[~longdispatch]


    dfloc.loc[:,lencol] = dfloc.eval('(end_hour - {})*3600'.format(start_time_col))

    dfloc.loc[:,timelocname], retbins = pd.qcut(dfloc[lencol],q = 2, retbins = True, precision = 0)
    dfloc.loc[:, 'Surge factor'] = dfloc.surge_factor #(dfloc.surge_factor*2.01).round()/2

    for en,func in enumerate(payment_function_names):
        print(en, func)
        evalstr2 = '{}_{}_earnings{}'.format(match_column.name.replace('_matched_index', ''), func, number_hours_next)
        evalstr1 = '{}_{}_earnings{}'.format('row_num', func, number_hours_next)

        if limit_to_matched_drivers_who_had_trip:
            dfloc = dfloc[dfloc[evalstr2]>0]

        dfloc.loc[:, func] = dfloc[evalstr1] - dfloc[evalstr2]
    keepcols = ['Surge factor', timelocname]
    keepcols.extend(payment_function_names)
    dfstacked = dfloc[keepcols].dropna().set_index(['Surge factor', timelocname]).stack()
    dfstacked= dfstacked.reset_index()
    dfstacked.loc[:,'Payment function'] = dfstacked['level_2'].map(func_pretty_names)
    dfstacked.loc[:,'Earnings difference'] = dfstacked[0]

    sns.set(font_scale=2.5)
    sns.set_style("white")
    sns.set_palette(sns.color_palette("cubehelix", 5))

    g = sns.relplot(data = dfstacked, x = 'Surge factor', y = 'Earnings difference', hue = timelocname, row = 'Payment function', kind = 'line', aspect = 2.5)
    plt.xlabel('Surge Factor')
    # plt.ylabel('Earnings difference')
    leg = g._legend
    leg.set_bbox_to_anchor([.35,.8])
    plt.legend(frameon = True)
    plt.ylim((-15, 60))
    if save_fig:
        label = 'tripindifference_bysurgelength_{}_{}{}_{}{}'.format(plt_label, match_column.name, number_hours_next, str(limit_to_matched_drivers_who_had_trip), distance_threshold)
        saveimage(label, extension = 'png')

    # plt.show()
    sns.set(font_scale=1)
    sns.set_style("white")
    sns.set_palette(sns.color_palette("cubehelix", 5))
    # for en,func in enumerate(payment_function_names):
    #     print(en, func)
    #     evalstr2 = '{}_{}_earnings{}'.format(match_column.name.replace('_matched_index', ''), func, number_hours_next)
    #     evalstr1 = '{}_{}_earnings{}'.format('row_num', func, number_hours_next)
    #
    #     lencol = 'ride_total_time_seconds'
    #
    #     dfloc = dffun[[evalstr1, evalstr2, 'surge_factor', lencol]].dropna()
    #
    #     dfloc.loc[:,timelocname], retbins = pd.qcut(dfloc[lencol],q = 2, retbins = True, precision = 0)
    #     dfloc.loc[:, 'surge_factor_rounded'] = (dfloc.surge_factor*2.01).round()/2 #round to nearest .5 (rounding .25,.75 up) for smoother plots
    #
    #     if limit_to_matched_drivers_who_had_trip:
    #         dfloc = dfloc[dfloc[evalstr2]>0]
    #
    #     dfloc.loc[:, 'differences'] = dfloc[evalstr1] - dfloc[evalstr2]
    #
    #     sns.lineplot(data = dfloc, x = 'surge_factor_rounded', y = 'differences', hue = timelocname)
    #     plt.xlabel('Surge Factor')
    #     plt.ylabel('Earnings increase from accepting request')
    #     plt.legend(frameon = False, loc = 'upper left')
    #     plt.ylim((-10, 60))
    #     if save_fig:
    #         label = 'tripindifference_bysurgelength_{}_{}_{}{}_{}_{}{}'.format(plt_label, func,match_column.name, number_hours_next, str(limit_to_matched_drivers_who_had_trip), distance_threshold)
    #         saveimage(label, extension = 'png')

def plot_trip_indifference_variance_by_addmult_interpolation(df, payment_function_add, payment_function_mult, number_hours_next, match_column, limit_to_matched_drivers_who_had_trip = True, func_filesave_names = func_filesave_names, func_pretty_names = func_pretty_names, plt_label = '', save_fig = False, distance_threshold = 1):

    dffun = df[df[match_column.name.replace('index', 'distance')] < distance_threshold]

    evalstr_add_1 = '{}_{}_earnings{}'.format('row_num', payment_function_add, number_hours_next)
    evalstr_add_2 = '{}_{}_earnings{}'.format(match_column.name.replace('_matched_index', ''), payment_function_add, number_hours_next)

    evalstr_mult_1 = '{}_{}_earnings{}'.format('row_num', payment_function_mult, number_hours_next)
    evalstr_mult_2 = '{}_{}_earnings{}'.format(match_column.name.replace('_matched_index', ''), payment_function_mult, number_hours_next)

    if limit_to_matched_drivers_who_had_trip:
        dffun = dffun[dffun[evalstr_add_2]>0]

    differences_add = dffun[evalstr_add_1] - dffun[evalstr_add_2]
    differences_mult = dffun[evalstr_mult_1] - dffun[evalstr_mult_2]

    differences_add = differences_add.dropna()
    differences_mult = differences_mult.dropna()

    interp = np.linspace(0, 1, 100)
    variances = []
    for x in interp:
        variances.append((differences_add*x + differences_mult*(1-x)).var())

    plt.plot(interp, variances)
    plt.xlabel('Fraction of surge component that is additive')
    plt.ylabel('Variance of trip indifference')
    if save_fig:
        label = 'tripindifference_variancebysurgefraction_{}_{}{}_{}{}'.format(plt_label, match_column.name, number_hours_next, str(limit_to_matched_drivers_who_had_trip), distance_threshold)
        saveimage(label, extension = 'png')
