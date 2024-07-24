###############################################################################
# 
#  Copyright (C) 2024, Northwestern University and Argonne National Laboratory
#  See COPYRIGHT notice in top-level directory.
# 
###############################################################################

from ._File cimport File
from._Dimension cimport Dimension

cdef class Variable:
    cdef public int _varid, _file_id, _nunlimdim
    cdef public File _file
    cdef public _name, ndim, dtype, xtype, mask, scale, always_mask, chartostring
