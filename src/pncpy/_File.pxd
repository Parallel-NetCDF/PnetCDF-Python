from ._Dimension cimport Dimension

cdef class File:
    cdef int ierr
    cdef public int _ncid
    cdef public int _isopen, indep_mode
    cdef public file_format, dimensions, variables