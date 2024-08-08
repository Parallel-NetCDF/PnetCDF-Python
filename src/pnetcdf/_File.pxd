###############################################################################
#
#  Copyright (C) 2024, Northwestern University and Argonne National Laboratory
#  See COPYRIGHT notice in top-level directory.
#
###############################################################################

from ._Dimension cimport Dimension

cdef class File:
    cdef int ierr
    cdef public int _ncid
    cdef public int _isopen, indep_mode
    cdef public file_format, dimensions, variables

cdef class Dataset(File):
    pass
