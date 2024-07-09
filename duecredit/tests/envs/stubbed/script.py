from due import due, Doi

kwargs = dict(
    entry=Doi("10.1007/s12021-008-9041-y"),
    description="Multivariate pattern analysis of neural data",
    tags=["use"]
)

import numpy as np

due.cite(path="test", **kwargs)


@due.dcite(**kwargs)
def method(arg):
    return arg+1

assert(method(1) == 2)
print("done123")
