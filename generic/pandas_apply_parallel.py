from multiprocessing import  Pool
from functools import partial
import numpy as np
import pandas as pd

#code from https://stackoverflow.com/questions/26784164/pandas-multiprocessing-apply
def _parallelize(data, func, num_of_processes=4):
    data_split = np.array_split(data, num_of_processes)
    pool = Pool(num_of_processes)
    data = pd.concat(pool.map(func, data_split))
    pool.close()
    pool.join()
    return data

def _run_on_subset(data_subset, func):
    return data_subset.apply(func, axis=1)


number_of_processors = 4

# def parallelize_on_rows(data, func, num_of_processes=4):
#     return _parallelize(data, partial(_run_on_subset, func = func), num_of_processes)

def set_number_of_processors(number):
    global number_of_processors
    number_of_processors = number

def parallelize_on_rows(data, func):
    return _parallelize(data, partial(_run_on_subset, func = func), number_of_processors)
