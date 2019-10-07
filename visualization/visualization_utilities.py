import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

from utilities import *
from generic.latexify import *
from payment.payment_functions import *


def plot_two_payments(df, payment1 = 'reverse_engineer_fare', payment2 = 'total_fare'):
    x = range(5, 500)
    print(payment1, payment2)
    plt.scatter(df[payment1], df[payment2])
    plt.plot(x, x)
    plt.xscale('log')
    plt.yscale('log')
    plt.show()

def print_mean_variance_trip_payments(dfs, payment_function_names):
    for df in dfs:
        for name in payment_function_names:
            print("{:<40}: {:.2f}, {:.2f} ".format(name, df[name].sum(), np.var(df[name])))
        print()


def plot_single_period_aggregation(df, func, number_hours_next, match_column, limit_to_matched_drivers_who_had_trip = True, bins = 20, func_filesave_names = func_filesave_names, func_pretty_names = func_pretty_names, plt_label = '', save_fig = False, distance_threshold = 1):

    dffun = df[df[match_column.name.replace('index', 'distance')] < distance_threshold]

    evalstr1 = '{0}_{1}hrsearnings'.format(func, number_hours_next)
    evalstr2 = '{2}_{0}_{1}hrsearnings'.format(func, number_hours_next, match_column.name.replace('_matched_index', ''))
    if limit_to_matched_drivers_who_had_trip:
        dfloc = dffun[dffun[evalstr2]>0]
        # return dfloc[differences == 0]
    else:
        dfloc = dffun

    dfloc = dfloc.dropna(subset = [evalstr1, evalstr2])

    dfloc[evalstr1].hist(cumulative = False, bins = bins, label = 'Row driver {}'.format(func_pretty_names.get(func, func.replace('_', ''))), alpha = .3)
    dfloc[evalstr2].hist(cumulative = False, bins = bins, label = 'Matched driver{}'.format(func_pretty_names.get(func, func.replace('_', ''))), alpha = .3)

    print('{}: {:.3}, {:.3}'.format(func, dfloc[evalstr1].mean(), dfloc[evalstr1].var()))
    print('{}: {:.3}, {:.3}'.format(func, dfloc[evalstr2].mean(), dfloc[evalstr2].var()))

    plt.legend(frameon = False, ncol = 1) #bbox_to_anchor=(1, 1.1)
    # if save_fig:
    #     label = 'tripindifference_{}_{}{}_{}_{}{}'.format(plt_label, match_column.name, number_hours_next, ''.join([func_filesave_names.get(func, func) for func in payment_function_names]), str(limit_to_matched_drivers_who_had_trip), distance_threshold)
    #     saveimage(label, extension = 'pdf')
