import numpy as np
from .params import Params

params = Params(2,1)
params.Q = np.array([1.0, 1.0])
params.reference_type = Params.ReferenceType.COS
params.amplitute = np.radians(60)
