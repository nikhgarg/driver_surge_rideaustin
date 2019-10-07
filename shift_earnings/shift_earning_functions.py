import pandas as pd
import numpy as np
from payment.payment_functions import *
from utilities import *
from generic.latexify import *

def get_session_earnings_df(df, payment_function_names, shift_column = 'active_driver_id'):
    df.loc[:, 'surged_trip'] = df.surged_trip.astype(int)
    df.loc[:, 'trip_duration'] = df.end_hour - df.start_hour

    aggdict = {x:lambda x: np.sum(x.tolist()) for x in payment_function_names} #propagates nan. While np.sum does propagate nan's for lists, lambda function needed because it does not propagate nan's for pandas series. This is apparently, "not a bug." https://github.com/numpy/numpy/issues/14424
    aggdict['dispatch_hour'] = 'min'
    aggdict['start_hour'] = 'min'
    aggdict['end_hour'] = 'max'
    aggdict['driver_id'] = 'count' # doesn't matter which column it is, I just want a count
    aggdict['surged_trip'] = 'sum' # number of surged trips
    aggdict['trip_duration'] = 'sum' # number of surged trips

    df_session = df.groupby(shift_column).agg(aggdict)
    df_session.rename(columns = {'driver_id' : 'number_trips'}, inplace = True)
    df_session.loc[:, 'session_length'] = df_session.eval('end_hour - dispatch_hour')

    df_session.loc[:,'Proportion on trip'] = df_session.eval('trip_duration/session_length')

    for func in payment_function_names:
        df_session.loc[:, '{}_perhour'.format(func)] = df_session.eval('{}/session_length'.format(func))

    return df_session

def print_weighted_mean_variance_session_earnings(df_session, payment_function_names):
    print('Per hour in session')
    for func in payment_function_names:
        print(func)
        print(weighted_mean_variance(df_session, '{}_perhour'.format(func), 'session_length'))
        print()

    print('Overall in session')
    for func in payment_function_names:
        print(func)
        print(weighted_mean_variance(df_session, '{}'.format(func), 'session_length'))
        print()

def plot_weighted_histogram_session_earnings(df_session, payment_function_names, func_filesave_names = func_filesave_names, func_pretty_names = func_pretty_names, plt_label = '', save_fig = False, colors = None):
    for per_hour in [True, False]:
        if per_hour:
            perhourstr = '_perhour'
            bins =np.logspace(.8, 2.5, 40)
        else:
            perhourstr = ''
            bins =np.logspace(.8, 3, 40)
        dfsession_valid = df_session.dropna()
        maxhist = 0
        for en, func in enumerate(payment_function_names):
            print(func)
            hist, bin_edges = np.histogram(dfsession_valid['{}{}'.format(func,perhourstr)], weights = dfsession_valid.session_length, bins = bins)
            maxhist = max([maxhist, max(hist)])
            # hist = [xx if xx>0 else .1 for xx in hist ]
            # print(hist)
            if colors is None:
                plt.bar(bin_edges[:-1], hist, width=np.diff(bin_edges), alpha = .3, label = func_pretty_names.get(func, func))
            else:
                plt.bar(bin_edges[:-1], hist, width=np.diff(bin_edges), alpha = .3, label = func_pretty_names.get(func, func), color = colors[en])


        plt.yscale('log', nonposy = 'clip')
        plt.ylim((1, maxhist*1.1))
        if not per_hour:
            plt.xscale('log')
        else:
            plt.xscale('log')

        plt.xlabel('{} shift earnings'.format('Per hour' if per_hour else 'Total'), fontsize = 20)
        plt.ylabel('Weighted number of shifts', fontsize = 20)
        plt.legend(frameon = False, bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=2, mode="expand", borderaxespad=0.)
        if save_fig:
            label = 'sessionearnings_{}_{}_{}'.format(plt_label, 'perhour' if per_hour else 'overall', ''.join([func_filesave_names.get(func, func) for func in payment_function_names]))
            saveimage(label, extension = 'png') #have to do png because pdf with log scale is giving an error

def plot_weighted_variance_session_earnings_by_addmult_interpolation(df_session, payment_function_add, payment_function_mult, plt_label, save_fig = False):
    dfsession_valid = df_session.dropna()

    interp = np.linspace(0, 1, 100)
    variances_perhourearnings = []
    variances_sessionearnings = []
    for x in interp:
        # get the interpolation for total sum using those two columns

        dfsession_valid.loc[:,'interpolated'] = dfsession_valid[payment_function_add]*x +  dfsession_valid[payment_function_mult]*(1-x)
        mean, variance = weighted_mean_variance(dfsession_valid, 'interpolated', 'session_length')
        variances_sessionearnings.append(variance)

        # then also get the per hour earnings by dividing by the session length
        dfsession_valid.loc[:,'interpolated_perhour'] = dfsession_valid.interpolated/dfsession_valid.session_length
        mean, variance = weighted_mean_variance(dfsession_valid, 'interpolated_perhour', 'session_length')
        variances_perhourearnings.append(variance)

    plt.plot(interp, variances_perhourearnings)
    plt.xlabel('Fraction of surge component that is additive')
    plt.ylabel('Shift per hour earnings variance')
    if save_fig:
        label = 'shiftearningsperhour_variancebysurgefraction_{}'.format(plt_label)
        saveimage(label, extension = 'pdf')
    else:
        plt.show()

    plt.plot(interp, variances_sessionearnings)
    plt.xlabel('Fraction of surge component that is additive')
    plt.ylabel('Shift earnings variance')
    if save_fig:
        label = 'shiftearnings_variancebysurgefraction_{}'.format(plt_label)
        saveimage(label, extension = 'pdf')
    else:
        plt.show()
