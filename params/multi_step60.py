import numpy as np
from .params import Params

params = Params(2,1)
params.tf = 2.5
params.amplitute = np.radians(60)
params.c_list = np.linspace(0, 1, 11)
