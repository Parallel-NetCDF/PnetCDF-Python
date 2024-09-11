###############################################################################
#
#  Copyright (C) 2024, Northwestern University and Argonne National Laboratory
#  See COPYRIGHT notice in top-level directory.
#
###############################################################################

# init for pnetcdf. package
# Docstring comes from extension module _PnetCDF.
__version__ = "1.0.0"
from ._File import *
from ._Dimension import *
from ._Variable import *
from ._utils import *

def libver():
    """
    libver()

    :return: The PnetCDF-Python version string, for example "1.0.0".
    :rtype: str
    """
    return __version__

