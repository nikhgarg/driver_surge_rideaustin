import pandas as pd
import scipy
from scipy import stats as stats
import numpy as np
from functools import partial
import copy
import seaborn as sns


# from generic.latexify import *
from generic.pandas_apply_parallel import *
from utilities import *
from payment.payment_functions import *
from payment.payment_function_templates import *




def distance_l1(df, paymentfunc1 = 'total_fare', paymentfunc2 = 'reverse_engineer_fare'):
    return (df[paymentfunc1] - df[paymentfunc2]).abs().sum(skipna = True)

def distance_sum(df, paymentfunc1 = 'reverse_engineer_fare', paymentfunc2 = 'pure_multiplicative_fare'):
    return (df[paymentfunc1] - df[paymentfunc2]).sum(skipna = True)

def plot_meanpayment_bysurgefactor(df, payment_function_names):
    df.groupby('surge_factor')[payment_function_names].agg('mean').plot()
    plt.legend(bbox_to_anchor=(1., 1))

def binary_search_to_find_parameter(df, payment_func, colname1, colname2, distance_func = distance_sum, min_param=0, max_param = 100, threshold = .001, print_stuff = True):
    valmidv = threshold + 1
    while abs(valmidv) > threshold:
        mid = (min_param + max_param)/2
        valmidv = distance_func(payment_func(df, mid), paymentfunc1 =colname1, paymentfunc2=colname2)
        if print_stuff: print( mid, valmidv )
        if valmidv > 0:
            min_param = mid
        else:
            max_param = mid
    return mid
