from ._Dimension cimport Dimension

cdef class File:
    cdef int ierr
    cdef public int _ncid
    cdef public int _isopen, def_mode_on, indep_mode
    cdef public data_model, path, dimensions, disk_format, variables