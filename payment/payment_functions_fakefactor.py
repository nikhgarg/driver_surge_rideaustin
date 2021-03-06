import pandas as pd
import numpy as np
from functools import partial

from payment.payment_function_templates import *

## Pure multiplicative and additive surge valid for entire 2 month reverse engineered dataset
additives_by_surge_withmin_fakefactor = {5.0: 11.679040174931288, 4.75: 9.453221736475825, 4.5: 9.588401101063937, 4.0: 9.615769982337952, 4.25: 9.594031726010144, 3.75: 9.957537893205881, 3.5: 9.92576852440834, 3.0: 10.548560321331024, 3.25: 10.640523582696915, 2.75: 10.865232348442078, 2.5: 11.063981056213379, 2.0: 12.741836905479431, 2.25: 12.023007869720459, 1.75: 11.503362655639648, 1.5: 14.593744277954102, 1.0: 50.0}


#payment function with min and base fare
withmin_additive_byfakesurgefactor = partial(withmin_additive_bysurgefactor_withparams, additives_by_surge = additives_by_surge_withmin_fakefactor, col_name = 'withmin_addsurge_byfakesurgefactor_fare')
