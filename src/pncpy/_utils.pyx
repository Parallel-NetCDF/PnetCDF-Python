include "PnetCDF.pxi"
from ._File cimport File
from cpython.mem cimport PyMem_Malloc, PyMem_Free
import numpy as np
from numpy.lib.stride_tricks import as_strided
from libc.stdlib cimport malloc, free
from mpi4py.libmpi cimport MPI_Offset
from mpi4py import MPI


"""cdef MPI.Datatype MPI_CHAR, MPI_BYTE, MPI_UNSIGNED_CHAR, MPI_SHORT, MPI_UNSIGNED_SHORT, MPI_INT, \
     MPI_UNSIGNED, MPI_INT64, MPI_UNSIGNED64, MPI_FLOAT, MPI_DOUBLE

MPI_Datatype MPI_CHAR = MPI.CHAR
MPI_Datatype MPI_INT8 = MPI.INT8
MPI_Datatype MPI_UNSIGNED8 = MPI.UINT8
MPI_Datatype MPI_INT16 = MPI.INT16
MPI_Datatype MPI_UNSIGNED16 = MPI.UINT16
MPI_Datatype MPI_INT32 = MPI.INT32
MPI_Datatype MPI_UNSIGNED32 = MPI.UINT32
MPI_Datatype MPI_INT64 = MPI.INT64
MPI_Datatype MPI_UNSIGNED64 = MPI.UINT64
MPI_Datatype MPI_FLOAT = MPI.FLOAT
MPI_Datatype MPI_DOUBLE = MPI.DOUBLE"""

import_array()

# np data type <--> netCDF data type mapping.
_nptonctype  = {'S1' : NC_CHAR_C,
                'i1' : NC_BYTE_C,
                'u1' : NC_UBYTE_C,
                'i2' : NC_SHORT_C,
                'u2' : NC_USHORT_C,
                'i4' : NC_INT_C,
                'u4' : NC_UINT_C,
                'i8' : NC_INT64_C,
                'u8' : NC_UINT64_C,
                'f4' : NC_FLOAT_C,
                'f8' : NC_DOUBLE_C}

_nptompitype = {'S1' : MPI_CHAR,
                'i1' : MPI_BYTE,
                'u1' : MPI_UNSIGNED_CHAR,
                'i2' : MPI_SHORT,
                'u2' : MPI_UNSIGNED_SHORT,
                'i4' : MPI_INT,
                'u4' : MPI_UNSIGNED,
                'i8' : MPI_LONG_LONG,
                'u8' : MPI_UNSIGNED_LONG_LONG,
                'f4' : MPI_FLOAT,
                'f8' : MPI_DOUBLE}


"""_nptompitype = {'S1' : MPI_CHAR,
                'i1' : MPI_INT8,
                'u1' : MPI_UNSIGNED8,
                'i2' : MPI_INT16,
                'u2' : MPI_UNSIGNED16,
                'i4' : MPI_INT32,
                'u4' : MPI_UNSIGNED32,
                'i8' : MPI_INT64,
                'u8' : MPI_UNSIGNED64,
                'f4' : MPI_FLOAT,
                'f8' : MPI_DOUBLE}"""

# CDF2 file: NC_UBYTE, NC_USHORT, NC_UINT, NC_INT64, and NC_UINT64 not supported
# Need to convert to supported dtypes first if possible
_notcdf2dtypes  = {'u1' : 'i1',
                'u2' : 'i2',
                'u4' : 'i4',
                'i8' : 'i4',
                'u8' : 'i4'}

# just integer types.
_intnptonctype  = {'i1' : NC_BYTE_C,
                   'u1' : NC_UBYTE_C,
                   'i2' : NC_SHORT_C,
                   'u2' : NC_USHORT_C,
                   'i4' : NC_INT_C,
                   'u4' : NC_UINT_C,
                   'i8' : NC_INT64_C,
                   'u8' : NC_UINT64_C}

# default fill_value to numpy datatype mapping.
default_fillvals = { 'S1':NC_FILL_CHAR_C,
                     'i1':NC_FILL_BYTE_C,
                     'u1':NC_FILL_UBYTE_C,
                     'i2':NC_FILL_SHORT_C,
                     'u2':NC_FILL_USHORT_C,
                     'i4':NC_FILL_INT_C,
                     'u4':NC_FILL_UINT_C,
                     'i8':NC_FILL_INT64_C,
                     'u8':NC_FILL_UINT64_C,
                     'f4':NC_FILL_FLOAT_C,
                     'f8':NC_FILL_DOUBLE_C}

_nctonptype = {}
for _key,_value in _nptonctype.items():
    _nctonptype[_value] = _key
_supportedtypes = _nptonctype.keys()
_supportedtypescdf2 = [t for t in _nptonctype if t not in _notcdf2dtypes]

# create dictionary mapping string identifiers to netcdf format codes
_reverse_format_dict = {
    NC_FORMAT_CLASSIC_C: "CLASSIC",
    NC_FORMAT_CDF2_C: "CDF2",
    NC_FORMAT_64BIT_OFFSET_C: "64BIT_OFFSET",
    NC_FORMAT_64BIT_C: "64BIT",
    NC_FORMAT_CDF5_C: "CDF5",
    NC_FORMAT_64BIT_DATA_C: "64BIT_DATA",
    NC_FORMAT_NETCDF4_C: "NETCDF4",
    NC_FORMAT_BP_C: "BP"
}
# create external NC datatype constants for python users
NC_CHAR = NC_CHAR_C
NC_BYTE = NC_BYTE_C
NC_UBYTE = NC_UBYTE_C
NC_SHORT = NC_SHORT_C
NC_USHORT = NC_USHORT_C
NC_INT = NC_INT_C
NC_UINT = NC_UINT_C
NC_INT64 = NC_INT64_C
NC_UINT64 = NC_UINT64_C
NC_FLOAT = NC_FLOAT_C
NC_DOUBLE = NC_DOUBLE_C

NC_REQ_ALL = NC_REQ_ALL_C
NC_GET_REQ_ALL = NC_GET_REQ_ALL_C
NC_PUT_REQ_ALL = NC_PUT_REQ_ALL_C
NC_REQ_NULL = NC_REQ_NULL_C
NC_FILL = NC_FILL_C
NC_NOFILL = NC_NOFILL_C

NC_FILL_BYTE = NC_FILL_BYTE_C
NC_FILL_CHAR = NC_FILL_CHAR_C
NC_FILL_SHORT = NC_FILL_SHORT_C
NC_FILL_INT = NC_FILL_INT_C
NC_FILL_FLOAT = NC_FILL_FLOAT_C
NC_FILL_DOUBLE = NC_FILL_DOUBLE_C
NC_FILL_UBYTE = NC_FILL_UBYTE_C
NC_FILL_USHORT = NC_FILL_USHORT_C
NC_FILL_UINT = NC_FILL_UINT_C
NC_FILL_INT64 = NC_FILL_INT64_C
NC_FILL_UINT64 = NC_FILL_UINT64_C

NC_FORMAT_CLASSIC = NC_FORMAT_CLASSIC_C
NC_FORMAT_CDF2 = NC_FORMAT_CDF2_C
NC_FORMAT_64BIT_OFFSET = NC_FORMAT_64BIT_OFFSET_C
NC_FORMAT_64BIT = NC_FORMAT_64BIT_C
NC_FORMAT_CDF5 = NC_FORMAT_CDF5_C
NC_FORMAT_64BIT_DATA = NC_FORMAT_64BIT_DATA_C
NC_FORMAT_NETCDF4 = NC_FORMAT_NETCDF4_C
NC_FORMAT_BP = NC_FORMAT_BP_C

NC_CLASSIC_MODEL = NC_CLASSIC_MODEL_C
NC_64BIT_OFFSET = NC_64BIT_OFFSET_C
NC_64BIT_DATA = NC_64BIT_DATA_C
NC_NETCDF4 = NC_NETCDF4_C
NC_BP = NC_BP_C

#Attributes that only exist at the python level (not in the netCDF file)
_private_atts = \
['_ncid','_varid','dimensions','variables', 'file_format',
 '_nunlimdim','path', 'name', '__orthogonal_indexing__', '_buffer']
# internal C functions.
cdef _strencode(pystr,encoding=""):
    # encode a string into bytes.  If already bytes, do nothing.
    # uses 'utf-8' for default encoding.
    if not encoding:
        encoding = 'utf-8'
    try:
        return pystr.encode(encoding)
    except (AttributeError, UnicodeDecodeError):
        return pystr # already bytes or unicode?

cdef _check_err(ierr, err_cls=RuntimeError, filename=""):
    # print netcdf error message, raise error.
    if ierr != NC_NOERR:
        err_str = (<char *>ncmpi_strerror(ierr)).decode('ascii')
        if issubclass(err_cls, OSError):
            if isinstance(filename, bytes):
                filename = filename.decode()
            raise err_cls(ierr, err_str, filename)
        else:
            raise err_cls(err_str)



cdef _set_att(file, int varid, name, value,\
              nc_type xtype=-99):
    # Private function to set an attribute name/value pair
    cdef int ierr, N, file_id
    cdef char *attname
    cdef char *datstring
    cdef char **string_ptrs
    cdef ndarray value_arr
    cdef MPI_Offset lenarr
    bytestr = _strencode(name)
    attname = bytestr
    file_id = file._ncid
    # put attribute value into a np array.
    value_arr = np.array(value)
    if value_arr.ndim > 1: # issue #841
        raise ValueError('multi-dimensional array attributes not supported')
    N = value_arr.size

    if value_arr.dtype.char in ['S','U']:
        # don't allow string array attributes in NETCDF3 files.
        if N > 1:
            msg='array string attributes not supported'
        if not value_arr.shape:
            dats = _strencode(value_arr.item())
        else:
            value_arr1 = value_arr.ravel()
            dats = _strencode(''.join(value_arr1.tolist()))
        lenarr = len(dats)
        datstring = dats
        # TODO: resolve the special case when set attribute to none(\177)
        with nogil:
            ierr = ncmpi_put_att_text(file_id, varid, attname, lenarr, datstring)
        _check_err(ierr, err_cls=AttributeError)
    # a 'regular' array type ('f4','i4','f8' etc)
    else:
        if file.file_format != "64BIT_DATA":
            #check if dtype meets CDF-5 variable standards
            if value_arr.dtype.str[1:] not in _supportedtypescdf2:
                raise TypeError, 'illegal data type for attribute %r, must be one of %s, got %s' % (attname, _supportedtypescdf2, value_arr.dtype.str[1:])
        #check if dtype meets CDF-5 variable standards
        elif value_arr.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type for attribute %r, must be one of %s, got %s' % (attname, _supportedtypes, value_arr.dtype.str[1:])

        if xtype == -99: # if xtype is not passed in as kwarg.
            xtype = _nptonctype[value_arr.dtype.str[1:]]
        lenarr = PyArray_SIZE(value_arr)
        with nogil:
            ierr = ncmpi_put_att(file_id, varid, attname, xtype, lenarr,
                PyArray_DATA(value_arr))
        _check_err(ierr, err_cls=AttributeError)


cdef _get_att(file, int varid, name, encoding='utf-8'):
    # Private function to get an attribute value given its name
    cdef int ierr, n, file_id, var_id
    cdef MPI_Offset att_len
    cdef char *attname
    cdef nc_type att_type
    cdef ndarray value_arr
    # attribute names are assumed to be utf-8
    bytestr = _strencode(name,encoding='utf-8')
    attname = bytestr
    file_id = file._ncid
    var_id = varid
    with nogil:
        ierr = ncmpi_inq_att(file_id, varid, attname, &att_type, &att_len)
    _check_err(ierr, err_cls=AttributeError)
    # attribute is a character or string ...
    if att_type == NC_CHAR_C:
        value_arr = np.empty(att_len,'S1')
        with nogil:
            ierr = ncmpi_get_att_text(file_id, varid, attname,
                    PyArray_BYTES(value_arr))
        _check_err(ierr, err_cls=AttributeError)
        if name == '_FillValue':
            # make sure _FillValue for character arrays is a byte on python 3
            pstring = value_arr.tobytes()
        else:
            pstring =\
            value_arr.tobytes().decode(encoding,errors='replace').replace('\x00','')
        return pstring
    else:
    # a regular numeric type.
        if att_type == NC_LONG_C:
            att_type = NC_INT_C
        try:
            type_att = _nctonptype[att_type] # see if it is a primitive type
            value_arr = np.empty(att_len,type_att)
        except KeyError:
            raise KeyError('attribute %s has unsupported datatype' % attname)
        with nogil:
            ierr = ncmpi_get_att(file_id, varid, attname, PyArray_BYTES(value_arr))
        _check_err(ierr, err_cls=AttributeError)
        if value_arr.shape == ():
            # return a scalar for a scalar array
            return value_arr.item()
        elif att_len == 1:
            # return a scalar for a single element array
            return value_arr[0]
        else:
            return value_arr


cdef _get_att_names(int file_id, int varid):
    # Private function to get all the attribute names in a group
    cdef int ierr, numatts, n
    cdef char namstring[NC_MAX_NAME+1]
    if varid == NC_GLOBAL:
        with nogil:
            ierr = ncmpi_inq_natts(file_id, &numatts)
    else:
        with nogil:
            ierr = ncmpi_inq_varnatts(file_id, varid, &numatts)
    _check_err(ierr, err_cls=AttributeError)
    attslist = []
    for n from 0 <= n < numatts:
        with nogil:
            ierr = ncmpi_inq_attname(file_id, varid, n, namstring)
        _check_err(ierr, err_cls=AttributeError)
        # attribute names are assumed to be utf-8
        attslist.append(namstring.decode('utf-8'))
    return attslist

cdef _tostr(s):
    try:
        ss = str(s)
    except:
        ss = s
    return ss

cdef _safecast(a,b):
    # check to see if array a can be safely cast
    # to array b.  A little less picky than np.can_cast.
    try:
        is_safe = ((a == b) | (np.isnan(a) & np.isnan(b))).all()
        #is_safe = np.allclose(a, b, equal_nan=True) # numpy 1.10.0
    except:
        try:
            is_safe = (a == b).all() # string arrays.
        except:
            is_safe = False
    return is_safe

cpdef chartostring(b,encoding='utf-8'):
    """
    chartostring(b,encoding='utf-8')

    Convert a character array to a string array with one less dimension.

    returns a numpy string array with datatype `'UN'` (or `'SN'`) and shape
    `b.shape[:-1]` where where `N=b.shape[-1]`.

    :param b: Input character array (numpy datatype `'S1'` or `'U1'`).
    Will be converted to a array of strings, where each string has a fixed
    length of `b.shape[-1]` characters.
    :type b: numpy.ndarray

    :param encoding: [Optional] Can be used to specify character encoding (default
    `utf-8`). If `encoding` is 'none' or 'bytes', a `np.string_` btye array is
    returned.
    :type encoding: str

    :rtype: numpy.ndarray

    """
    dtype = b.dtype.kind
    if dtype not in ["S","U"]:
        raise ValueError("type must be string or unicode ('S' or 'U')")
    if encoding in ['none','None','bytes']:
        bs = b.tobytes()
    else:
        bs = b.tobytes().decode(encoding)
    slen = int(b.shape[-1])
    if encoding in ['none','None','bytes']:
        a = np.array([bs[n1:n1+slen] for n1 in range(0,len(bs),slen)],'S'+repr(slen))
    else:
        a = np.array([bs[n1:n1+slen] for n1 in range(0,len(bs),slen)],'U'+repr(slen))
    a.shape = b.shape[:-1]
    return a

cpdef stringtochar(a,encoding='utf-8'):
    """
    stringtochar(a,encoding='utf-8')

    Convert a string array to a character array with one extra dimension.

    Returns a numpy character array with datatype `'S1'` or `'U1'`
    and shape `a.shape + (N,)`, where N is the length of each string in a.

    :param a: Input numpy string array with numpy datatype `'SN'` or `'UN'`, where N
    is the number of characters in each string.  Will be converted to
    an array of characters (datatype `'S1'` or `'U1'`) of shape `a.shape + (N,)`.
    :type a: numpy.ndarray

    :param encoding: [Optional] Can be used to specify character encoding (default
    `utf-8`). If `encoding` is 'none' or 'bytes', a `numpy.string_` the input array
    is treated a raw byte strings (`numpy.string_`).
    :type encoding: str
    """
    dtype = a.dtype.kind
    if dtype not in ["S","U"]:
        raise ValueError("type must string or unicode ('S' or 'U')")
    if encoding in ['none','None','bytes']:
        b = np.array(tuple(a.tobytes()),'S1')
    else:
        b = np.array(tuple(a.tobytes().decode(encoding)),dtype+'1')
    b.shape = a.shape + (a.itemsize,)
    return b

cdef _StartCountStride(elem, shape, dimensions=None, file=None, datashape=None,\

        put=False):
    """Return start, count, stride and indices needed to store/extract data
    into/from a netCDF variable.

    This function is used to convert a slicing expression into a form that is
    compatible with the nc_get_vars function. Specifically, it needs
    to interpret integers, slices, Ellipses, and 1-d sequences of integers
    and booleans.

    Numpy uses "broadcasting indexing" to handle array-valued indices.
    "Broadcasting indexing" (a.k.a "fancy indexing") treats all multi-valued
    indices together to allow arbitrary points to be extracted. The index
    arrays can be multidimensional, and more than one can be specified in a
    slice, as long as they can be "broadcast" against each other.
    This style of indexing can be very powerful, but it is very hard
    to understand, explain, and implement (and can lead to hard to find bugs).
    Most other python packages and array processing
    languages use "orthogonal indexing" which only allows for 1-d index arrays and
    treats these arrays of indices independently along each dimension.

    The implementation of "orthogonal indexing" used here requires that
    index arrays be 1-d boolean or integer. If integer arrays are used,
    the index values must be sorted and contain no duplicates.

    In summary, slicing netcdf variable objects with 1-d integer or boolean arrays 
    is allowed, but may give a different result than slicing a numpy array.

    Numpy also supports slicing an array with a boolean array of the same
    shape. For example x[x>0] returns a 1-d array with all the positive values of x.
    This is also not supported in pnetcdf, if x.ndim > 1.

    Orthogonal indexing can be used in to select netcdf variable slices
    using the dimension variables. For example, you can use v[lat>60,lon<180]
    to fetch the elements of v obeying conditions on latitude and longitude.
    Allow for this sort of simple variable subsetting is the reason we decided to
    deviate from numpy's slicing rules.

    This function is used both by the __setitem__ and __getitem__ method of
    the Variable class.

    Parameters
    ----------
    elem : tuple of integer, slice, ellipsis or 1-d boolean or integer
    sequences used to slice the netCDF Variable (Variable[elem]).
    shape : tuple containing the current shape of the netCDF variable.
    dimensions : sequence
      The name of the dimensions.
      __setitem__.
    file  : netCDF File instance
      The netCDF file to which the variable being set belongs to.
    datashape : sequence
      The shape of the data that is being stored. Only needed by __setitem__
    put : True|False (default False).  If called from __setitem__, put is True.

    Returns
    -------
    start : ndarray (..., n)
      A starting indices array of dimension n+1. The first n
      dimensions identify different independent data chunks. The last dimension
      can be read as the starting indices.
    count : ndarray (..., n)
      An array of dimension (n+1) storing the number of elements to get.
    stride : ndarray (..., n)
      An array of dimension (n+1) storing the steps between each datum.
    indices : ndarray (..., n)
      An array storing the indices describing the location of the
      data chunk in the target/source array (__getitem__/__setitem__).

    Notes:

    netCDF data is accessed via the function:
       nc_get_vars(fileid, varid, start, count, stride, data)

    Assume that the variable has dimension n, then

    start is a n-tuple that contains the indices at the beginning of data chunk.
    count is a n-tuple that contains the number of elements to be accessed.
    stride is a n-tuple that contains the step length between each element.

    """
    # Adapted from netcdf4-python (https://unidata.github.io/netcdf4-python/)

    nDims = len(shape)
    if nDims == 0:
        nDims = 1
        shape = (1,)

    # is there an unlimited dimension? (only defined for __setitem__)
    if put:
        hasunlim = False
        unlimd={}
        if dimensions:
            for i in range(nDims):
                dimname = dimensions[i]
                # is this dimension unlimited?
                # look in current group, and parents for dim.
                dim = file.dimensions[dimname]
                unlimd[dimname]=dim.isunlimited()
                if unlimd[dimname]:
                    hasunlim = True
    else:
        hasunlim = False

    # When a single array or (non-tuple) sequence of integers is given
    # as a slice, assume it applies to the first dimension,
    # and use ellipsis for remaining dimensions.
    if np.iterable(elem):
        if type(elem) == np.ndarray or (type(elem) != tuple and \
            np.array([_is_int(e) for e in elem]).all()):
            elem = [elem]
            for n in range(len(elem)+1,nDims+1):
                elem.append(slice(None,None,None))
    else:   # Convert single index to sequence
        elem = [elem]

    # ensure there is at most 1 ellipse
    #  we cannot use elem.count(Ellipsis), as with fancy indexing would occur
    #  np.array() == Ellipsis which gives ValueError: The truth value of an
    #  array with more than one element is ambiguous. Use a.any() or a.all()
    if sum(1 for e in elem if e is Ellipsis) > 1:
        raise IndexError("At most one ellipsis allowed in a slicing expression")

    # replace boolean arrays with sequences of integers.
    newElem = []
    IndexErrorMsg=\
    "only integers, slices (`:`), ellipsis (`...`), and 1-d integer or boolean arrays are valid indices"
    i=0
    for e in elem:
        # string-like object try to cast to int
        # needs to be done first, since strings are iterable and
        # hard to distinguish from something castable to an iterable numpy array.
        if type(e) in [str, bytes]:
            try:
                e = int(e)
            except:
                raise IndexError(IndexErrorMsg)
        ea = np.asarray(e)
        # Raise error if multidimensional indexing is used.
        if ea.ndim > 1:
            raise IndexError("Index cannot be multidimensional")
        # set unlim to True if dimension is unlimited and put==True
        # (called from __setitem__)
        if hasunlim and put and dimensions:
            try:
                dimname = dimensions[i]
                unlim = unlimd[dimname]
            except IndexError: # more slices than dimensions (issue 371)
                unlim = False
        else:
            unlim = False
        # convert boolean index to integer array.
        if np.iterable(ea) and ea.dtype.kind =='b':
            # check that boolean array not too long
            if not unlim and shape[i] != len(ea):
                msg="""
                    Boolean array must have the same shape as the data along this dimension."""
                raise IndexError(msg)
            ea = np.flatnonzero(ea)
        # an iterable (non-scalar) integer array.
        if np.iterable(ea) and ea.dtype.kind == 'i':
            # convert negative indices in 1d array to positive ones.
            ea = np.where(ea < 0, ea + shape[i], ea)
            if np.any(ea < 0):
                raise IndexError("integer index out of range")
            # if unlim, let integer index be longer than current dimension
            # length.
            if ea.shape != (0,):
                elen = shape[i]
                if unlim:
                    elen = max(ea.max()+1,elen)
                if ea.max()+1 > elen:
                    msg="integer index exceeds dimension size"
                    raise IndexError(msg)
            newElem.append(ea)
        # integer scalar
        elif ea.dtype.kind == 'i':
            newElem.append(e)
        # slice or ellipsis object
        elif type(e) == slice or type(e) == type(Ellipsis):
            newElem.append(e)
        else:  # castable to a scalar int, otherwise invalid
            try:
                e = int(e)
                newElem.append(e)
            except:
                raise IndexError(IndexErrorMsg)
        if type(e)==type(Ellipsis):
            i+=1+nDims-len(elem)
        else:
            i+=1
    elem = newElem

    # replace Ellipsis and integer arrays with slice objects, if possible.
    newElem = []
    for e in elem:
        ea = np.asarray(e)
        # Replace ellipsis with slices.
        if type(e) == type(Ellipsis):
            # The ellipsis stands for the missing dimensions.
            newElem.extend((slice(None, None, None),) * (nDims - len(elem) + 1))
        # Replace sequence of indices with slice object if possible.
        elif np.iterable(e) and len(e) > 1:
            start = e[0]
            stop = e[-1]+1
            step = e[1]-e[0]
            try:
                ee = range(start,stop,step)
            except ValueError: # start, stop or step is not valid for a range
                ee = False
            if ee and len(e) == len(ee) and (e == np.arange(start,stop,step)).all():
                # don't convert to slice unless abs(stride) == 1
                # (nc_get_vars is very slow, issue #680)
                newElem.append(slice(start,stop,step))
            else:
                newElem.append(e)
        elif np.iterable(e) and len(e) == 1:
            newElem.append(slice(e[0], e[0] + 1, 1))
        else:
            newElem.append(e)
    elem = newElem

    # If slice doesn't cover all dims, assume ellipsis for rest of dims.
    if len(elem) < nDims:
        for n in range(len(elem)+1,nDims+1):
            elem.append(slice(None,None,None))

    # make sure there are not too many dimensions in slice.
    if len(elem) > nDims:
        raise ValueError("slicing expression exceeds the number of dimensions of the variable")

    # Compute the dimensions of the start, count, stride and indices arrays.
    # The number of elements in the first n dimensions corresponds to the
    # number of times the _get method will be called.
    sdim = []
    for i, e in enumerate(elem):
        # at this stage e is a slice, a scalar integer, or a 1d integer array.
        # integer array:  _get call for each True value
        if np.iterable(e):
            sdim.append(len(e))
        # Scalar int or slice, just a single _get call
        else:
            sdim.append(1)

    # broadcast data shape when assigned to full variable (issue #919)
    try:
        fullslice = elem.count(slice(None,None,None)) == len(elem)
    except: # fails if elem contains a numpy array.
        fullslice = False
    if fullslice and datashape and put and not hasunlim:
        datashape = broadcasted_shape(shape, datashape)

    # pad datashape with zeros for dimensions not being sliced (issue #906)
    # only used when data covers slice over subset of dimensions
    if datashape and len(datashape) != len(elem) and\
       len(datashape) == sum(1 for e in elem if type(e) == slice):
        datashapenew = (); i=0
        for e in elem:
            if type(e) != slice and not np.iterable(e): # scalar integer slice
                datashapenew = datashapenew + (0,)
            else: # slice object
                datashapenew = datashapenew + (datashape[i],)
                i+=1
        datashape = datashapenew

    # Create the start, count, stride and indices arrays.

    sdim.append(max(nDims, 1))
    start = np.empty(sdim, dtype=np.intp)
    count = np.empty(sdim, dtype=np.intp)
    stride = np.empty(sdim, dtype=np.intp)
    indices = np.empty(sdim, dtype=object)

    for i, e in enumerate(elem):

        ea = np.asarray(e)

        # set unlim to True if dimension is unlimited and put==True
        # (called from __setitem__). Note: grp and dimensions must be set.
        if hasunlim and put and dimensions:
            dimname = dimensions[i]
            unlim = unlimd[dimname]
        else:
            unlim = False

        #    SLICE    #
        if type(e) == slice:

            # determine length parameter for slice.indices.

            # shape[i] can be zero for unlim dim that hasn't been written to
            # yet.
            # length of slice may be longer than current shape
            # if dimension is unlimited (and we are writing, not reading).
            if unlim and e.stop is not None and e.stop > shape[i]:
                length = e.stop
            elif unlim and e.stop is None and datashape != ():
                try:
                    if e.start is None:
                        length = datashape[i]
                    else:
                        length = e.start+datashape[i]
                except IndexError:
                    raise IndexError("shape of data does not conform to slice")
            else:
                if unlim and datashape == () and len(dim) == 0:
                    # writing scalar along unlimited dimension using slicing
                    # syntax (var[:] = 1, when var.shape = ())
                    length = 1
                else:
                    length = shape[i]

            beg, end, inc = e.indices(length)
            n = len(range(beg,end,inc))

            start[...,i] = beg
            count[...,i] = n
            stride[...,i] = inc
            indices[...,i] = slice(None)

        #    ITERABLE    #
        elif np.iterable(e) and np.array(e).dtype.kind in 'i':  # Sequence of integers
            start[...,i] = np.apply_along_axis(lambda x: e*x, i, np.ones(sdim[:-1]))
            indices[...,i] = np.apply_along_axis(lambda x: np.arange(sdim[i])*x, i, np.ones(sdim[:-1], int))

            count[...,i] = 1
            stride[...,i] = 1

        #   all that's left is SCALAR INTEGER    #
        else:
            if e >= 0:
                start[...,i] = e
            elif e < 0 and (-e <= shape[i]) :
                start[...,i] = e+shape[i]
            else:
                raise IndexError("Index out of range")

            count[...,i] = 1
            stride[...,i] = 1
            indices[...,i] = -1    # Use -1 instead of 0 to indicate that
                                       # this dimension shall be squeezed.

    return start, count, stride, indices#, out_shape

cdef _out_array_shape(count):
    """Return the output array shape given the count array created by getStartCountStride"""

    s = list(count.shape[:-1])
    out = []

    for i, n in enumerate(s):
        if n == 1 and count.size > 0:
            c = count[..., i].ravel()[0] # All elements should be identical.
            out.append(c)
        else:
            out.append(n)
    return out

cdef broadcasted_shape(shp1, shp2):
    # determine shape of array of shp1 and shp2 broadcast against one another.
    x = np.array([1])
    # trick to define array with certain shape that doesn't allocate all the
    # memory.
    a = as_strided(x, shape=shp1, strides=[0] * len(shp1))
    b = as_strided(x, shape=shp2, strides=[0] * len(shp2))
    return np.broadcast(a, b).shape

cdef _is_int(a):
    try:
        return int(a) == a
    except:
        return False

cdef _get_format(int ncid):
    # Private function to get the netCDF file format
    cdef int ierr, formatp
    with nogil:
        ierr = ncmpi_inq_format(ncid, &formatp)
    _check_err(ierr)
    if formatp not in _reverse_format_dict:
        raise ValueError('format not supported by python interface')
    return _reverse_format_dict[formatp]
# external C functions.
cpdef strerror(err_code):
    """
    strerror(err_code)

    The function strerror returns a static reference to an error message string corresponding 
    to an integer netCDF error status or to a system error number, presumably returned by a previous
    call to some other PnetCDF function. 

    :param err_code: An error status that might have been returned from a previous call 
    to some PnetCDF function.
    :type err_code: int.

    :rtype: str

    """
    cdef int ierr
    ierr = err_code

    err_str = (<char *>ncmpi_strerror(ierr)).decode('ascii')
    return err_str

cpdef strerrno(err_code):
    """
    strerror(err_code)

    The function strerrno returns a character string containing the name of the NC error code. 
    For instance, ncmpi_strerrno(NC_EBADID) returns string "NC_EBADID". 

    :param err_code: An error status that might have been returned from a previous call 
    to some PnetCDF function.
    :type err_code: int.

    :rtype: str

    """
    cdef int ierr
    ierr = err_code
    err_code_str = (<char *>ncmpi_strerrno(ierr)).decode('ascii')
    return err_code_str

cpdef set_default_format(int new_format):
    """
    set_default_format(int new_format)

    The function  allows the user to change the format of the netCDF file to be created by future 
    calls to ncmpi_create without specifying the file format. It returns the existing default 
    format while setting a new default format. 

    :param new_format: ``pncpy.NC_FORMAT_CLASSIC`` (the default setting), ``pncpy.NC_FORMAT_CDF2`` 
    (``pncpy.NC_FORMAT_64BIT``), or ``pncpy.NC_FORMAT_CDF5`` (``pncpy.NC_FORMAT_64BIT_DATA``).

    :rtype: int

    Operational mode: This function is an independent subroutine, but is expected to be called by all processes that
    intend to create a file later.


    """
    cdef int ierr, newformat, oldformat
    newformat = new_format
    with nogil:
        ierr = ncmpi_set_default_format(newformat, &oldformat)
    _check_err(ierr)
    return oldformat

cpdef inq_default_format():
    """
    inq_default_format()

    The function returns the current setting for default file format.

    :rtype: int 

    Operational mode: This function is an independent subroutine.

    """
    cdef int curformat
    with nogil:
        ierr = ncmpi_inq_default_format(&curformat)
    _check_err(ierr)
    return curformat

cpdef inq_file_format(str file_name):
    """
    inq_file_format(str file_name)

    The function returns the current setting for default file format.

    :rtype: int 

    Operational mode: This function is an independent subroutine.

    """
    cdef char *filename
    cdef int ierr, curformat
    filename_bytestr =  _strencode(file_name)
    filename = filename_bytestr
    with nogil:
        ierr = ncmpi_inq_file_format(filename, &curformat)
    _check_err(ierr)
    return curformat

cpdef inq_malloc_max_size():
    """
    inq_malloc_max_size()

    Return the maximum size in bytes of memory allocated internally
    :rtype: int
    """
    cdef int ierr
    cdef int size
    with nogil:
        ierr = ncmpi_inq_malloc_max_size(<MPI_Offset *>&size)
    _check_err(ierr)
    return size

cpdef inq_malloc_size():
    """
    inq_malloc_size()

    Return the size in bytes of current memory allocated internally
    :rtype: int
    """
    cdef int ierr
    cdef int size
    with nogil:
        ierr = ncmpi_inq_malloc_size(<MPI_Offset *>&size)
    _check_err(ierr)
    return size
"""
cpdef inq_files_opened(ncids=None):
    cdef int ierr, num
    cdef int *ncidp
    
    with nogil:
        ierr = ncmpi_inq_files_opened(&num, NULL)
    _check_err(ierr)
    if ncids is not None:
        ncidp = <int *>malloc(sizeof(int) * num)
        with nogil:
            ierr = ncmpi_inq_files_opened(&num, ncidp)
        _check_err(ierr)
        for i in range(num):
            ncids[i] = ncidp[i]
    return num
"""
