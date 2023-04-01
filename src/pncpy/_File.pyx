import sys
import os
import subprocess
import warnings
include "PnetCDF.pxi"

cimport mpi4py.MPI as MPI
from mpi4py.libmpi cimport MPI_Comm, MPI_Info, MPI_Comm_dup, MPI_Info_dup, \
                               MPI_Comm_free, MPI_Info_free, MPI_INFO_NULL,\
                               MPI_COMM_WORLD



from libc.string cimport memcpy, memset
from libc.stdlib cimport malloc, free

from ._Dimension cimport Dimension
from ._Variable cimport Variable
from ._utils cimport _strencode, _check_err, _set_att, _get_att, _get_att_names
from._utils cimport _nctonptype
import numpy as np

#TODO: confirm the final list of private attributes
_private_atts = \
['_ncid','_varid','dimensions','variables','data_model','disk_format',
 '_nunlimdim','path', 'name', '__orthogoral_indexing__', '_buffer']

ctypedef MPI.Comm Comm
ctypedef MPI.Info Info

cdef class File:
    def __init__(self, filename, mode="w", format=None, clobber=True, Comm comm=None, Info info=None, **kwargs):
        """
        **`__init__(self, filename, format='64BIT_OFFSET', clobber=True, mode="w", Comm comm=None, Info info=None, **kwargs)`**

        `File` constructor.

        **`filename`**: Name of PnetCDF file to hold dataset.

        **`mode`**: access mode. `r` means read-only; no data can be
        modified. `w` means write; a new file is created, an existing file with
        the same name is deleted. `x` means write, but fail if an existing
        file with the same name already exists. `a` and `r+` mean append;
        an existing file is opened for reading and writing, if
        file does not exist already, one is created.


        **`clobber`**: if `True` (default), opening a file with `mode='w'`
        will clobber an existing file with the same name.  if `False`, an
        exception will be raised if a file with the same name already exists.
        mode=`x` is identical to mode=`w` with clobber=False.

        **`format`**: underlying file format (one of `'64BIT_OFFSET'` or
        `'64BIT_DATA'`.
        Only relevant if `mode = 'w'` (if `mode = 'r','a'` or `'r+'` the file format
        is automatically detected).
        """
        cdef int ncid
        encoding = sys.getfilesystemencoding()
        cdef char* path
        cdef MPI_Comm mpicomm = MPI_COMM_WORLD
        cdef MPI_Info mpiinfo = MPI_INFO_NULL
        cdef int cmode

        if comm is not None:
            mpicomm = comm.ob_mpi
        if info is not None:
            mpiinfo = info.ob_mpi
        bytestr = _strencode(filename, encoding=encoding)
        path = bytestr
        if format:
            supported_formats = ["64BIT_OFFSET", "64BIT_DATA"]
            if format not in supported_formats:
                msg="underlying file format must be one of `'64BIT_OFFSET'` or `'64BIT_DATA'`"
                raise ValueError(msg)

        # mode='x' is the same as mode='w' with clobber=False
        if mode == 'x':
            mode = 'w'
            clobber = False

        if mode == 'w' or (mode in ['a','r+'] and not os.path.exists(filename)):
            cmode = 0
            if not clobber:
                cmode = NC_NOCLOBBER
            if format in ['64BIT_OFFSET', '64BIT_DATA']:
                file_cmode = NC_64BIT_OFFSET if format  == '64BIT_OFFSET' else NC_64BIT_DATA
                cmode = cmode | file_cmode
            with nogil:
                ierr = ncmpi_create(mpicomm, path, cmode, mpiinfo, &ncid)

        elif mode == "r":
            with nogil:
                ierr = ncmpi_open(mpicomm, path, NC_NOWRITE, mpiinfo, &ncid)

        elif mode in ['a','r+'] and os.path.exists(filename):
            with nogil:
                ierr = ncmpi_open(mpicomm, path, NC_WRITE, mpiinfo, &ncid)
        else:
            raise ValueError("mode must be 'w', 'x', 'r', 'a' or 'r+', got '%s'" % mode)


        _check_err(ierr, err_cls=OSError, filename=path)
        self._isopen = 1
        self.def_mode_on = 0
        self.indep_mode = 0
        self._ncid = ncid
        self.data_model = format
        self.dimensions = _get_dims(self)
        self.variables = _get_vars(self)
    
    def close(self):
        self._close(True)
    
    def _close(self, check_err):
        cdef int ierr
        with nogil:
            ierr = ncmpi_close(self._ncid)

        if check_err:
            _check_err(ierr)

        self._isopen = 0 # indicates file already closed, checked by __dealloc__

    def filepath(self,encoding=None):
        """
        **`filepath(self,encoding=None)`**

        Get the file system path (or the opendap URL) which was used to
        open/create the Dataset. Requires netcdf >= 4.1.2.  The path
        is decoded into a string using `sys.getfilesystemencoding()` by default, this can be
        changed using the `encoding` kwarg."""
        cdef int ierr
        cdef int pathlen
        cdef char *c_path
        if encoding is None:
            encoding = sys.getfilesystemencoding()
        with nogil:
            ierr = ncmpi_inq_path(self._ncid, &pathlen, NULL)
        _check_err(ierr)

        c_path = <char *>malloc(sizeof(char) * (pathlen + 1))
        if not c_path:
            raise MemoryError()
        try:
            with nogil:
                ierr = ncmpi_inq_path(self._ncid, &pathlen, c_path)
            _check_err(ierr)

            py_path = c_path[:pathlen] # makes a copy of pathlen bytes from c_string
        finally:
            free(c_path)
        return py_path.decode(encoding)


    def __dealloc__(self):
        # close file when there are no references to object left
        if self._isopen:
           self._close(False)

    def __enter__(self):
        return self
    def __exit__(self,atype,value,traceback):
        self.close()

    def sync(self):
        """
        **`sync(self)`**

        Writes all buffered data in the `File` to the disk file."""
        cdef int ierr
        with nogil:
            ierr = ncmpi_sync(self._ncid)
        _check_err(ierr)

    def redef(self):
        self._redef()

    def _redef(self):
        cdef int ierr
        cdef int fileid= self._ncid
        if not self.def_mode_on:
            self.def_mode_on = 1
            with nogil:
                ierr = ncmpi_redef(fileid)
    def enddef(self):
        self._enddef()

    def _enddef(self):
        cdef int ierr
        cdef int fileid = self._ncid
        if self.def_mode_on:
            self.def_mode_on = 0
            with nogil:
                ierr = ncmpi_enddef(fileid)

    def begin_indep(self):
        cdef int ierr
        cdef int fileid = self._ncid
        with nogil:
            ierr = ncmpi_begin_indep_data(fileid)
        _check_err(ierr)
        self.indep_mode = 1

    def end_indep(self):
        cdef int ierr
        cdef int fileid = self._ncid
        with nogil:
            ierr = ncmpi_end_indep_data(fileid)
        _check_err(ierr)
        self.indep_mode = 0



    def defineDim(self, dimname, size=-1):
        """
        **`defineDim(self, dimname, size=-1)`**
        Creates a new dimension with the given `dimname` and `size`.
        `size` must be a positive integer or `-1`, which stands for
        "unlimited" (default is `-1`). Specifying a size of 0 also
        results in an unlimited dimension. The return value is the `Dimension`
        class instance describing the new dimension.  To determine the current
        maximum size of the dimension, use the `len` function on the `Dimension`
        instance. To determine if a dimension is 'unlimited', use the
        `Dimension.isunlimited` method of the `Dimension` instance.
        """
        self.dimensions[dimname] = Dimension(self, dimname, size=size)
        return self.dimensions[dimname]
    
    def defineVar(self, varname, nc_dtype, dimensions=(), fill_value=None):

        """
        **`defineVar(self, varname, datatype, dimensions=(), least_significant_digit=None,
        significant_digits=None, fill_value=None)`**

        Creates a new variable with the given `varname`, `datatype`, and
        `dimensions`. If dimensions are not given, the variable is assumed to be
        a scalar.

        The `datatype` can be a numpy datatype object, or a string that describes
        a numpy dtype object (like the `dtype.str` attribute of a numpy array).
        Supported specifiers include: `'S1' or 'c' (NC_CHAR), 'i1' or 'b' or 'B'
        (NC_BYTE), 'u1' (NC_UBYTE), 'i2' or 'h' or 's' (NC_SHORT), 'u2'
        (NC_USHORT), 'i4' or 'i' or 'l' (NC_INT), 'u4' (NC_UINT), 'i8' (NC_INT64),
        'u8' (NC_UINT64), 'f4' or 'f' (NC_FLOAT), 'f8' or 'd' (NC_DOUBLE)`.
        Data from netCDF variables is presented to python as numpy arrays with
        the corresponding data type.

        `dimensions` must be a tuple containing `Dimension` instances and/or
        dimension names (strings) that have been defined
        previously using `Dataset.defineDim`. The default value
        is an empty tuple, which means the variable is a scalar.

        The optional keyword `fill_value` can be used to override the default
        netCDF `_FillValue` (the value that the variable gets filled with before
        any data is written to it, defaults given in the dict `netCDF4.default_fillvals`).
        If fill_value is set to `False`, then the variable is not pre-filled.

        The return value is the `Variable` class instance describing the new
        variable.

        A list of names corresponding to netCDF variable attributes can be
        obtained with the `Variable` method `Variable.ncattrs`. A dictionary
        containing all the netCDF attribute name/value pairs is provided by
        the `__dict__` attribute of a `Variable` instance.

        `Variable` instances behave much like array objects. Data can be
        assigned to or retrieved from a variable with indexing and slicing
        operations on the `Variable` instance. A `Variable` instance has six
        Dataset standard attributes: `dimensions, dtype, shape, ndim, name`. 
        Application programs should never modify these attributes. The `dimensions`
            attribute is a tuple containing the
        names of the dimensions associated with this variable. The `dtype`
        attribute is a string describing the variable's data type (`i4, f8,
        S1,` etc). The `shape` attribute is a tuple describing the current
        sizes of all the variable's dimensions. The `name` attribute is a
        string containing the name of the Variable instance. The `ndim` attribute
        is the number of variable dimensions.
        """
        # if dimensions is a single string or Dimension instance,
        # convert to a tuple.
        # This prevents a common error that occurs when
        # dimensions = 'lat' instead of ('lat',)
        if isinstance(dimensions, (str, bytes, Dimension)):
            dimensions = dimensions,
        # convert elements of dimensions tuple to Dimension
        # instances if they are strings.
        # _find_dim looks for dimension in this file, and if not
        # found there, looks in parent (and it's parent, etc, back to root).
        dimensions =\
        tuple(self.dimensions[d] if isinstance(d,(str,bytes)) else d for d in dimensions)
        # create variable.
        self.variables[varname] = Variable(self, varname, nc_dtype,
        dimensions=dimensions, fill_value=fill_value)
        return self.variables[varname]
    

    def ncattrs(self):
        """
        **`ncattrs(self)`**

        return netCDF attribute names for this File in a list."""
        return _get_att_names(self._ncid, NC_GLOBAL)
    def setncattr(self,name,value):
        """
        **`setncattr(self,name,value)`**

        set a netCDF file attribute using name,value pair.
        Use if you need to set a netCDF attribute with the
        with the same name as one of the reserved python attributes."""
        cdef nc_type xtype
        xtype=-99

        #TODO: decide whether or not need to exit define mode for user
        if not self.def_mode_on:
            self.redef()
            _set_att(self, NC_GLOBAL, name, value, xtype=xtype)
            self.enddef()
        else:
            _set_att(self, NC_GLOBAL, name, value, xtype=xtype)
    def getncattr(self,name,encoding='utf-8'):
        """
        **`getncattr(self,name)`**

        retrieve a netCDF dataset or group attribute.
        Use if you need to get a netCDF attribute with the same
        name as one of the reserved python attributes.

        option kwarg `encoding` can be used to specify the
        character encoding of a string attribute (default is `utf-8`)."""
        return _get_att(self, NC_GLOBAL, name, encoding=encoding)

    def __delattr__(self,name):
        # if it's a netCDF attribute, remove it
        if name not in _private_atts:
            self.delncattr(name)
        else:
            raise AttributeError(
            "'%s' is one of the reserved attributes %s, cannot delete. Use delncattr instead." % (name, tuple(_private_atts)))


    def delncattr(self, name):
        """
        **`delncattr(self,name,value)`**

        delete a netCDF file attribute.  Use if you need to delete a
        netCDF attribute with the same name as one of the reserved python
        attributes."""
        cdef char *attname
        cdef int ierr
        bytestr = _strencode(name)
        attname = bytestr
        if not self.def_mode_on:
            self._redef()
            with nogil:
                ierr = ncmpi_del_att(self._ncid, NC_GLOBAL, attname)
            self._enddef()
        else:
            ierr = ncmpi_del_att(self._ncid, NC_GLOBAL, attname)
        _check_err(ierr)

    def __setattr__(self,name,value):
    # if name in _private_atts, it is stored at the python
    # level and not in the netCDF file.
        if name not in _private_atts:
            self.setncattr(name, value)
        elif not name.endswith('__'):
            if hasattr(self,name):
                raise AttributeError(
            "'%s' is one of the reserved attributes %s, cannot rebind. Use setncattr instead." % (name, tuple(_private_atts)))
            else:
                self.__dict__[name]=value

    def __getattr__(self,name):
        # if name in _private_atts, it is stored at the python
        # level and not in the netCDF file.
        if name.startswith('__') and name.endswith('__'):
            # if __dict__ requested, return a dict with netCDF attributes.
            if name == '__dict__':
                names = self.ncattrs()
                values = []
                for name in names:
                    values.append(_get_att(self, NC_GLOBAL, name))
                return dict(zip(names, values))
            else:
                raise AttributeError
        elif name in _private_atts:
            return self.__dict__[name]
        else:
            return self.getncattr(name)
            
    def renameAttribute(self, oldname, newname):
        """
        **`renameAttribute(self, oldname, newname)`**

        rename a `File` attribute named `oldname` to `newname`."""
        cdef char *oldnamec
        cdef char *newnamec
        cdef int ierr
        cdef int _file_id
        _file_id = self._ncid
        bytestr = _strencode(oldname)
        oldnamec = bytestr
        bytestr = _strencode(newname)
        newnamec = bytestr
        
        with nogil:
            ierr = ncmpi_rename_att(_file_id, NC_GLOBAL, oldnamec, newnamec)
        _check_err(ierr)
    def _wait(self, num=None, requests=None, collective=False):
        cdef int _file_id, ierr
        cdef int num_req
        cdef int *requestp
        cdef int *statusp
        _file_id = self._ncid

        if isinstance(num, int):
            requestp = <int *>malloc(sizeof(int) * num)
            statusp = <int *>malloc(sizeof(int) * num)
            for n from 0 <= n < num:
                requestp[n] = requests[n]
            num_req = num
            if not collective:
                with nogil:
                    ierr = ncmpi_wait(_file_id, num_req, requestp, statusp)
            else:
                with nogil:
                    ierr = ncmpi_wait_all(_file_id, num_req, requestp, statusp)
            status = [statusp[i] for i in range(num)]
            return status
        else:
            if num is None or num == "REQ_ALL":
                num_req = NC_REQ_ALL
            elif num == "GET_REQ_ALL":
                num_req = NC_GET_REQ_ALL
            elif num == "PUT_REQ_ALL":
                num_req = NC_PUT_REQ_ALL
            if not collective:
                with nogil:
                    ierr = ncmpi_wait(_file_id, num_req, NULL, NULL)
            else:
                with nogil:
                    ierr = ncmpi_wait_all(_file_id, num_req, NULL, NULL)
            _check_err(ierr)
            return None

    def wait(self, num=None, requests=None):
        return self._wait(num, requests, collective=False)
    def wait_all(self, num=None, requests=None):
        return self._wait(num, requests, collective=True)


cdef _get_dims(file):
    # Private function to create `Dimension` instances for all the
    # dimensions in a `File`
    cdef int ierr, numdims, n, _file_id
    cdef int *dimids
    cdef char namstring[NC_MAX_NAME+1]
    # get number of dimensions in this file.
    _file_id = file._ncid
    with nogil:
        ierr = ncmpi_inq_ndims(_file_id, &numdims)
    _check_err(ierr)
    # create empty dictionary for dimensions.
    dimensions = dict()
    if numdims > 0:
        dimids = <int *>malloc(sizeof(int) * numdims)
        for n from 0 <= n < numdims:
            dimids[n] = n
        for n from 0 <= n < numdims:
            with nogil:
                ierr = ncmpi_inq_dimname(_file_id, dimids[n], namstring)
            _check_err(ierr)
            name = namstring.decode('utf-8')
            dimensions[name] = Dimension(file = file, name = name, id=dimids[n])
        free(dimids)
    return dimensions


cdef _get_vars(file):
    # Private function to create `Variable` instances for all the
    # variables in a `File` 
    cdef int ierr, numvars, n, nn, numdims, varid, classp, iendian, _file_id
    cdef int *varids
    cdef int *dimids
    cdef nc_type xtype
    cdef char namstring[NC_MAX_NAME+1]
    cdef char namstring_cmp[NC_MAX_NAME+1]
    # get number of variables in this File.
    _file_id = file._ncid
    with nogil:
        ierr = ncmpi_inq_nvars(_file_id, &numvars)
    _check_err(ierr, err_cls=AttributeError)
    # create empty dictionary for variables.
    variables = dict()
    if numvars > 0:
        # get variable ids.
        varids = <int *>malloc(sizeof(int) * numvars)
        for n from 0 <= n < numvars:
            varids[n] = n
        # loop over variables.
        for n from 0 <= n < numvars:
            varid = varids[n]
            # get variable name.
            with nogil:
                ierr = ncmpi_inq_varname(_file_id, varid, namstring)
            _check_err(ierr)
            name = namstring.decode('utf-8')
            # get variable type.
            with nogil:
                ierr = ncmpi_inq_vartype(_file_id, varid, &xtype)
            _check_err(ierr)
            # check to see if it is a supported user-defined type.
            try:
                datatype = _nctonptype[xtype]
            except KeyError:
                msg="WARNING: variable '%s' has unsupported datatype, skipping .." % name
                warnings.warn(msg)
                continue
            # get number of dimensions.
            with nogil:
                ierr = ncmpi_inq_varndims(_file_id, varid, &numdims)
            _check_err(ierr)
            dimids = <int *>malloc(sizeof(int) * numdims)
            # get dimension ids.
            with nogil:
                ierr = ncmpi_inq_vardimid(_file_id, varid, dimids)
            _check_err(ierr)
            dimensions = []
            for nn from 0 <= nn < numdims:
                for key, value in file.dimensions.items():
                    if value._dimid == dimids[nn]:
                        dimensions.append(value)
                        break

            # create variable instance
            variables[name] = Variable(file, name, xtype, dimensions, id=varid)
        free(varids) # free pointer holding variable ids.
    return variables