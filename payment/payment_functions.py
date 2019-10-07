import pandas as pd
import numpy as np
from functools import partial

from payment.payment_function_templates import *

#Note: Surge functions that have different multipliers/additives per surge factor, so that the overall payment during each surge remains the same, as in the theory

# Reverse engineering the total_fare, without the 2 dollar addition that is not going to driver
payment_reverse_engineer = partial (reverse_engineer_withparams, multiplier = rev_eng_mult, additive = 0, col_name = 'mimic_fare')

## Pure multiplicative and additive surge valid for entire 2 month reverse engineered dataset
multipliers_by_surge = {1.0: 1.178897671343293, 1.25: 1.2159457663074136, 1.5: 1.2160108075477183, 2.0: 1.2208759784698486, 1.75: 1.2208770494908094, 2.25: 1.2109917122870684, 2.5: 1.2150291353464127, 3.0: 1.2011436047032475, 2.75: 1.1996255721896887, 3.25: 1.1975256726145744, 3.5: 1.1947848368436098, 4.0: 1.1625474784523249, 3.75: 1.1804979294538498, 4.25: 1.1852897703647614, 4.5: 1.1432667262852192, 5.0: 1.1957231909036636}
additives_by_surge = {1.0: 50.0, 1.25: 9.453221783041954, 1.5: 9.58840111270547, 2.0: 9.615769982337952, 1.75: 9.59403170272708, 2.25: 9.957537800073624, 2.5: 9.92576852440834, 3.0: 10.548560321331024, 2.75: 10.640523582696915, 3.25: 10.865232348442078, 3.5: 11.063981056213379, 4.0: 12.741836160421371, 3.75: 12.023007869720459, 4.25: 11.503374576568604, 4.5: 14.593739807605743, 5.0: 11.09071969985962}
pure_multiplicative_bysurgefactor = partial(pure_multiplicative_bysurgefactor_withparams, multipliers_by_surge=multipliers_by_surge, col_name = 'pure_mult_bysurgefactor_fare')
pure_additive_bysurgefactor = partial(pure_additive_bysurgefactor_withparams, additives_by_surge=additives_by_surge, multipliers_by_surge=multipliers_by_surge, col_name = 'pure_addsurge_bysurgefactor_fare')


## Pure multiplicative and additive surge valid for 10 hours of peak surge
multipliers_by_surge_10hrs = {2.0: 1.2199825141578913, 1.75: 1.2184856459498405, 2.25: 1.2028269469738007, 1.5: 1.1831541545689106, 1.0: 1.1087017133831978, 1.25: 1.1369101703166962, 2.5: 1.1962052434682846, 2.75: 1.1761847883462906, 3.0: 1.1756353080272675, 3.25: 1.199445128440857, 3.5: 1.1748194694519043, 3.75: 1.186758279800415, 4.0: 1.1583805084228516, 4.5: 1.1570930480957031}
additives_by_surge_10hrs = {2.0: 9.505422785878181, 1.75: 9.625808894634247, 2.25: 10.010084509849548, 1.5: 11.15148589015007, 1.0: 50.0, 1.25: 14.945030212402344, 2.5: 10.335464775562286, 2.75: 11.482319235801697, 3.0: 11.691039800643921, 3.25: 10.655009746551514, 3.5: 12.554585933685303, 3.75: 10.171842575073242, 4.0: 11.826705932617188, 4.5: 11.9171142578125}
pure_multiplicative_bysurgefactor_10hrs = partial(pure_multiplicative_bysurgefactor_withparams, multipliers_by_surge=multipliers_by_surge_10hrs, col_name = 'pure_mult_bysurgefactor_10hrs_fare')
pure_additive_bysurgefactor_10hrs = partial(pure_additive_bysurgefactor_withparams, additives_by_surge=additives_by_surge_10hrs, multipliers_by_surge=multipliers_by_surge_10hrs, col_name = 'pure_addsurge_bysurgefactor_10hrs_fare')

## Pure multiplicative and additive surge valid for 24 hours of peak surge
multipliers_by_surge_24hrs = {1.5: 1.1865070788189769, 1.0: 1.1202968191355467, 1.25: 1.1699369177222252, 1.75: 1.2114460114389658, 2.0: 1.217248709872365, 2.25: 1.2031899765133858, 2.5: 1.1957576498389244, 2.75: 1.1753834784030914, 3.0: 1.1808238923549652, 3.25: 1.1959418654441833, 3.5: 1.185755804181099, 3.75: 1.1589720845222473, 4.0: 1.154230535030365, 4.5: 1.1471375823020935, 5.0: 1.1644408106803894}
additives_by_surge_24hrs = {1.5: 10.914454236626625, 1.0: 50.0, 1.25: 11.674657464027405, 1.75: 9.867240488529205, 2.0: 9.610043466091156, 2.25: 10.00046506524086, 2.5: 10.356885194778442, 2.75: 11.515563726425171, 3.0: 11.410433053970337, 3.25: 10.576212406158447, 3.5: 11.692538857460022, 3.75: 13.512396812438965, 4.0: 12.933921813964844, 4.5: 14.520883560180664, 5.0: 14.776110649108887}
pure_multiplicative_bysurgefactor_24hrs = partial(pure_multiplicative_bysurgefactor_withparams, multipliers_by_surge=multipliers_by_surge_24hrs, col_name = 'pure_mult_bysurgefactor_24hrs_fare')
pure_additive_bysurgefactor_24hrs = partial(pure_additive_bysurgefactor_withparams, additives_by_surge=additives_by_surge_24hrs, multipliers_by_surge=multipliers_by_surge_24hrs, col_name = 'pure_addsurge_bysurgefactor_24hrs_fare')


## Pure multiplicative and additive surge valid for 3 weeks
multipliers_by_surge_3weeks = {1.0: 1.1671877175103873, 1.25: 1.2075823324266821, 1.5: 1.2091127573512495, 1.75: 1.2157325050793588, 2.75: 1.196974329650402, 2.5: 1.2103931978344917, 2.0: 1.2178884935565293, 2.25: 1.201058248989284, 3.5: 1.1930283159017563, 3.0: 1.1994396802037954, 3.25: 1.1951863765716553, 4.25: 1.2054145336151123, 3.75: 1.1837195605039597, 4.0: 1.151891052722931, 4.5: 1.1600546538829803, 5.0: 1.1957231909036636}
additives_by_surge_3weeks = {1.0: 50.0, 1.25: 9.766680374741554, 1.5: 9.84233096241951, 1.75: 9.72050204873085, 2.75: 10.660051554441452, 2.5: 9.999258816242218, 2.0: 9.663368202745914, 2.25: 10.235638543963432, 3.5: 11.154604703187943, 3.0: 10.585768520832062, 3.25: 10.938781499862671, 4.25: 9.975481033325195, 3.75: 11.661297082901001, 4.0: 13.611799478530884, 4.5: 13.149338960647583, 5.0: 11.09071969985962}
pure_multiplicative_bysurgefactor_3weeks = partial(pure_multiplicative_bysurgefactor_withparams, multipliers_by_surge=multipliers_by_surge_3weeks, col_name = 'pure_mult_bysurgefactor_3weeks_fare')
pure_additive_bysurgefactor_3weeks = partial(pure_additive_bysurgefactor_withparams, additives_by_surge=additives_by_surge_3weeks, multipliers_by_surge=multipliers_by_surge_3weeks, col_name = 'pure_addsurge_bysurgefactor_3weeks_fare')


# Lists with the payment functions
payment_functions_mimicfares = [payment_reverse_engineer]
payment_function_mimicfares_names = ['mimic_fare']

payment_functions_10hrs = [payment_reverse_engineer,pure_multiplicative_bysurgefactor_10hrs, pure_additive_bysurgefactor_10hrs]
payment_function_10hrs_names = ['mimic_fare', 'pure_mult_bysurgefactor_10hrs_fare', 'pure_addsurge_bysurgefactor_10hrs_fare']

payment_functions_24hrs = [payment_reverse_engineer,pure_multiplicative_bysurgefactor_24hrs, pure_additive_bysurgefactor_24hrs]
payment_function_24hrs_names = ['mimic_fare', 'pure_mult_bysurgefactor_24hrs_fare', 'pure_addsurge_bysurgefactor_24hrs_fare']

payment_functions_3weeks = [payment_reverse_engineer,pure_multiplicative_bysurgefactor_3weeks, pure_additive_bysurgefactor_3weeks]
payment_function_3weeks_names = ['mimic_fare', 'pure_mult_bysurgefactor_3weeks_fare', 'pure_addsurge_bysurgefactor_3weeks_fare']

payment_functions_2months = [payment_reverse_engineer,pure_multiplicative_bysurgefactor, pure_additive_bysurgefactor]
payment_function_2months_names = ['mimic_fare', 'pure_mult_bysurgefactor_fare', 'pure_addsurge_bysurgefactor_fare']

all_names = list(set([x for y in [payment_function_10hrs_names, payment_function_24hrs_names, payment_function_3weeks_names, payment_function_2months_names] for x in y]))
func_filesave_names = {x: x.replace('_', '').replace('bysurgefactor', 'BSF') for x in all_names}

func_pretty_names = {'mimic_fare': 'Existing Payment',
                        'pure_mult_bysurgefactor_fare': 'Multiplicative Surge',
                        'pure_addsurge_bysurgefactor_fare':'Additive Surge',
                        'pure_mult_bysurgefactor_10hrs_fare':'Multiplicative Surge',
                        'pure_addsurge_bysurgefactor_10hrs_fare':'Additive Surge',
                        'pure_mult_bysurgefactor_24hrs_fare':'Multiplicative Surge',
                        'pure_addsurge_bysurgefactor_24hrs_fare':'Additive Surge',
                        'pure_mult_bysurgefactor_3weeks_fare':'Multiplicative Surge',
                        'pure_addsurge_bysurgefactor_3weeks_fare':'Additive Surge',
}
