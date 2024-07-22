from ._File cimport File
from._Dimension cimport Dimension

cdef class Variable:
    cdef public int _varid, _file_id, _nunlimdim
    cdef public File _file
    cdef public _name, ndim, dtype, xtype, mask, scale, always_mask, chartostring