include "PnetCDF.pxi"
cdef _check_err(ierr, err_cls=*, filename=*)
cdef _strencode(pystr, encoding=*)
cdef _set_att(file, int varid, name, value, nc_type xtype=*)
cdef _get_att(file, int varid, name, encoding=*)
cdef _get_att_names(int file_id, int varid)
cdef _nptonctype, _notcdf2dtypes, _nctonptype, _nptompitype, _supportedtypes, _supportedtypescdf2, default_fillvals,
cdef _tostr(s)
cdef _safecast(a,b)
cdef _StartCountStride(elem, shape, dimensions=*, file=*, datashape=*,\
        put=*)
cdef _out_array_shape(count)
cdef chartostring(b,encoding=*)
cdef stringtochar(a,encoding=*)

