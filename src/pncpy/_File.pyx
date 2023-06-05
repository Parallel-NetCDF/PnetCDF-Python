import sys
import os
import subprocess
import warnings
include "PnetCDF.pxi"

cimport mpi4py.MPI as MPI
from mpi4py.libmpi cimport MPI_Comm, MPI_Info, MPI_Comm_dup, MPI_Info_dup, \
                               MPI_Comm_free, MPI_Info_free, MPI_INFO_NULL,\
                               MPI_COMM_WORLD, MPI_Offset



from libc.string cimport memcpy, memset
from libc.stdlib cimport malloc, free

from ._Dimension cimport Dimension
from ._Variable cimport Variable
from ._utils cimport _strencode, _check_err, _set_att, _get_att, _get_att_names, _get_format
from._utils cimport _nctonptype
import numpy as np

#TODO: confirm the final list of private attributes
_private_atts = \
['_ncid','_varid','dimensions','variables', 'file_format',
 '_nunlimdim','path', 'name', '__orthogoral_indexing__', '_buffer']

ctypedef MPI.Comm Comm
ctypedef MPI.Info Info


cdef class File:
    def __init__(self, filename, mode="w", format=None, Comm comm=None, Info info=None, **kwargs):
        """
        __init__(self, filename, format='64BIT_OFFSET', mode="w", Comm comm=None, Info info=None, **kwargs)

        The constructor for :class:`pncpy.File`.

        :param filename: Name of the new file.
        :type filename: str

        :param mode: Access mode.

            - ``r``: Opens a file for reading, error if the file does not exist.
            - ``w``: Opens a file for writing, creates the file if it does not exist.
            - ``x``: Creates the file, returns an error if the file exists.
            -  ``a`` and ``r+``: append, creates the file if it does not exist.
        
        :type mode: str

        :param format: underlying file format. Only relevant if ``mode`` is ``w`` or ``x``.

            - ``64BIT_OFFSET``: NetCDF-2 format.
            - ``64BIT_DATA``: NetCDF-5 format.
            - `None` defaults to default file format (NetCDF-1 format)

        :type format: str

        :param comm: MPI communicator to use for file access. `None` defaults to MPI_COMM_WORLD.
        :type comm: mpi4py.MPI.Comm or None

        :param info: MPI info object to use for file access. `None` defaults to MPI_INFO_NULL.
        :type info: mpi4py.MPI.Info or None
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
        
        clobber = True
        # mode='x' is the same as mode='w' with clobber=False
        if mode == 'x':
            mode = 'w'
            clobber = False

        if mode == 'w' or (mode in ['a','r+'] and not os.path.exists(filename)):
            cmode = 0
            if not clobber:
                cmode = NC_NOCLOBBER
            if format in ['64BIT_OFFSET', '64BIT_DATA']:
                file_cmode = NC_64BIT_OFFSET_C if format  == '64BIT_OFFSET' else NC_64BIT_DATA_C
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
        self.indep_mode = 0
        self._ncid = ncid
        self.file_format = _get_format(ncid)
        self.dimensions = _get_dims(self)
        self.variables = _get_variables(self)
    
    def close(self):
        """
        close(self)
        """
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
        filepath(self,encoding=None)

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
        sync(self)

        Writes all buffered data in the `File` to the disk file."""
        cdef int ierr
        with nogil:
            ierr = ncmpi_sync(self._ncid)
        _check_err(ierr)

    def redef(self):
        """
        redef(self)
        """
        self._redef()

    def _redef(self):
        cdef int ierr
        cdef int fileid= self._ncid
        with nogil:
            ierr = ncmpi_redef(fileid)
        _check_err(ierr)
    def enddef(self):
        """
        enddef(self)
        """
        self._enddef()

    def _enddef(self):
        cdef int ierr
        cdef int fileid = self._ncid
        with nogil:
            ierr = ncmpi_enddef(fileid)
        _check_err(ierr)

    def begin_indep(self):
        """
        begin_indep(self)
        """
        cdef int ierr
        cdef int fileid = self._ncid
        with nogil:
            ierr = ncmpi_begin_indep_data(fileid)
        _check_err(ierr)
        self.indep_mode = 1

    def end_indep(self):
        """
        end_indep(self)
        """
        cdef int ierr
        cdef int fileid = self._ncid
        with nogil:
            ierr = ncmpi_end_indep_data(fileid)
        _check_err(ierr)
        self.indep_mode = 0

    def flush(self):
        """
        flush(self)
        """
        cdef int ierr
        cdef int fileid = self._ncid
        with nogil:
            ierr = ncmpi_flush(fileid)
        _check_err(ierr)


    def def_dim(self, dimname, size=-1):
        """
        def_dim(self, dimname, size=-1)

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
    
    def rename_var(self, oldname, newname):
        """
        rename_var(self, oldname, newname)

        rename a `Variable` named `oldname` to `newname`
        """
        cdef char *namstring
        cdef Variable var
        cdef int _file_id, _varid
        try:
            var = self.variables[oldname]
        except KeyError:
            raise KeyError('%s not a valid variable name' % oldname)
        bytestr = _strencode(newname)
        namstring = bytestr
        _file_id = self._ncid
        _var_id = var._varid
        with nogil:
            ierr = ncmpi_rename_var(_file_id, _var_id, namstring)
        _check_err(ierr)
        # remove old key from dimensions dict.
        self.variables.pop(oldname)
        # add new key.
        self.variables[newname] = var

    def rename_dim(self, oldname, newname):
        """
        rename_var(self, oldname, newname)

        rename a `Dimension` named `oldname` to `newname`
        """
        cdef char *namstring
        cdef Variable var
        cdef int _file_id, _dim_id
        try:
            dim = self.dimensions[oldname]
        except KeyError:
            raise KeyError('%s not a valid dimension name' % oldname)
        bytestr = _strencode(newname)
        namstring = bytestr
        _file_id = self._ncid
        _dim_id = dim._dimid
        with nogil:
            ierr = ncmpi_rename_dim(_file_id, _dim_id, namstring)
        _check_err(ierr)
        # remove old key from dimensions dict.
        self.dimensions.pop(oldname)
        # add new key.
        self.dimensions[newname] = dim


    def def_var(self, varname, nc_dtype, dimensions=(), fill_value=None):
        """
        defineVar(self, varname, nc_dtype, dimensions=(), fill_value=None)

        Create a new variable with the given parameters.

        :param varname: Name of the new variable.
        :type varname: str

        :param nc_dtype: The datatype of the new variable. Supported string specifiers are: 

            - ``S1`` or ``c`` for NC_CHAR
            - ``i1`` or ``b`` or ``B`` for NC_BYTE
            - ``u1`` for NC_UBYTE
            - ``i2`` or ``h`` or ``s`` for NC_SHORT
            - ``u2`` for NC_USHORT
            - ``i4`` or ``i`` or ``l`` for NC_INT
            - ``u4`` for NC_UINT
            - ``i8`` for NC_INT64
            - ``u8`` for NC_UINT64
            - ``f4`` or ``f`` for NC_FLOAT
            - ``f8`` or ``d`` for NC_DOUBLE
        :type nc_dtype: str or numpy.dtype

        :param dimensions: The dimensions of the new variable. Empty tuple suggests a scalar.

        :type dimensions: tuple of str or :class:`pncpy.Dimension` instances
        
        :param fill_value: The fill value of the new variable. Accepted values are:

            - ``None``: use the default fill value for the given datatype
            - ``False``: fill mode is turned off
            - any other value: use the given value as fill value

        :return: The created variable.
        :rtype: :class:`pncpy.Variable`
        """

        # the following should be added to explaination of variable class.
        # # A list of names corresponding to netCDF variable attributes can be
        # # obtained with the `Variable` method `Variable.ncattrs`. A dictionary
        # # containing all the netCDF attribute name/value pairs is provided by
        # # the `__dict__` attribute of a `Variable` instance.

        # # `Variable` instances behave much like array objects. Data can be
        # # assigned to or retrieved from a variable with indexing and slicing
        # # operations on the `Variable` instance. A `Variable` instance has six
        # # Dataset standard attributes: `dimensions, dtype, shape, ndim, name`. 
        # # Application programs should never modify these attributes. The `dimensions`
        # #     attribute is a tuple containing the
        # # names of the dimensions associated with this variable. The `dtype`
        # # attribute is a string describing the variable's data type (`i4, f8,
        # # S1,` etc). The `shape` attribute is a tuple describing the current
        # # sizes of all the variable's dimensions. The `name` attribute is a
        # # string containing the name of the Variable instance. The `ndim` attribute
        # # is the number of variable dimensions.
        # # """

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
        ncattrs(self)

        return netCDF attribute names for this File in a list."""
        return _get_att_names(self._ncid, NC_GLOBAL)

    def put_att(self,name,value):
        """
        put_att(self,name,value)

        set a netCDF file attribute using name,value pair.
        Use if you need to set a netCDF attribute with the
        with the same name as one of the reserved python attributes."""
        cdef nc_type xtype
        xtype=-99
        _set_att(self, NC_GLOBAL, name, value, xtype=xtype)

    def get_att(self,name,encoding='utf-8'):
        """
        get_att(self,name)

        retrieve a netCDF dataset or file attribute.
        Use if you need to get a netCDF attribute with the same
        name as one of the reserved python attributes.

        option kwarg `encoding` can be used to specify the
        character encoding of a string attribute (default is `utf-8`)."""
        return _get_att(self, NC_GLOBAL, name, encoding=encoding)

    def __delattr__(self,name):
        # if it's a netCDF attribute, remove it
        if name not in _private_atts:
            self.del_att(name)
        else:
            raise AttributeError(
            "'%s' is one of the reserved attributes %s, cannot delete. Use del_att instead." % (name, tuple(_private_atts)))

    def del_att(self, name):
        """
        del_att(self,name,value)

        delete a netCDF file attribute.  Use if you need to delete a
        netCDF attribute with the same name as one of the reserved python
        attributes."""
        cdef char *attname
        cdef int ierr
        bytestr = _strencode(name)
        attname = bytestr
        with nogil:
            ierr = ncmpi_del_att(self._ncid, NC_GLOBAL, attname)
        _check_err(ierr)

    def __setattr__(self,name,value):
    # if name in _private_atts, it is stored at the python
    # level and not in the netCDF file.
        if name not in _private_atts:
            self.put_att(name, value)
        elif not name.endswith('__'):
            if hasattr(self,name):
                raise AttributeError(
            "'%s' is one of the reserved attributes %s, cannot rebind. Use put_att instead." % (name, tuple(_private_atts)))
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
            return self.get_att(name)
            
    def rename_att(self, oldname, newname):
        """
        rename_att(self, oldname, newname)

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

    def _wait(self, num=None, requests=None, status=None, collective=False):
        cdef int _file_id, ierr
        cdef int num_req
        cdef int *requestp
        cdef int *statusp
        _file_id = self._ncid
        if num is None:
            num = NC_REQ_ALL_C
        if num in [NC_REQ_ALL_C, NC_PUT_REQ_ALL_C, NC_GET_REQ_ALL_C]:
            num_req = num
            if not collective:
                with nogil:
                    ierr = ncmpi_wait(_file_id, num_req, NULL, NULL)
            else:
                with nogil:
                    ierr = ncmpi_wait_all(_file_id, num_req, NULL, NULL)
            _check_err(ierr)
        else:
            requestp = <int *>malloc(sizeof(int) * num)
            statusp = <int *>malloc(sizeof(int) * num)
            num_req = num
            for n from 0 <= n < num:
                requestp[n] = requests[n]
            if not collective:
                with nogil:
                    ierr = ncmpi_wait(_file_id, num_req, requestp, statusp)
            else:
                with nogil:
                    ierr = ncmpi_wait_all(_file_id, num_req, requestp, statusp)
            for n from 0 <= n < num:
                requests[n] = requestp[n]

            if status is not None:
                for n from 0 <= n < num:
                    status[n] = statusp[n]
            _check_err(ierr)
        return None

    def wait(self, num=None, requests=None, status=None):
        """
        wait(self, num=None, requests=None, status=None)

        """
        return self._wait(num, requests, status, collective=False)

    def wait_all(self, num=None, requests=None, status=None):
        """
        wait_all(self, num=None, requests=None, status=None)
        
        """
        return self._wait(num, requests, status, collective=True)

    def cancel(self, num=None, requests=None, status=None):
        """
        cancel(self, num=None, requests=None, status=None)
        
        """
        cdef int _file_id, ierr
        cdef int num_req
        cdef int *requestp
        cdef int *statusp
        _file_id = self._ncid
        if num is None:
            num = NC_REQ_ALL_C
        if num in [NC_REQ_ALL_C, NC_PUT_REQ_ALL_C, NC_GET_REQ_ALL_C]:
            num_req = num
            with nogil:
                ierr = ncmpi_cancel(_file_id, num_req, NULL, NULL)
            _check_err(ierr)
        else:
            requestp = <int *>malloc(sizeof(int) * num)
            statusp = <int *>malloc(sizeof(int) * num)
            num_req = num
            for n from 0 <= n < num:
                requestp[n] = requests[n]
            with nogil:
                ierr = ncmpi_cancel(_file_id, num_req, requestp, statusp)
            for n from 0 <= n < num:
                requests[n] = requestp[n]
            if status is not None:
                for n from 0 <= n < num:
                    status[n] = statusp[n]
            _check_err(ierr)


    def get_nreqs(self):
        """
        get_nreqs(self)
        
        """
        cdef int _file_id, ierr
        cdef int num_req
        _file_id = self._ncid
        with nogil:
            ierr = ncmpi_inq_nreqs(_file_id, &num_req)
        _check_err(ierr)
        return num_req

    def attach_buff(self, bufsize = None):
        """
        attach_buff(self, bufsize = None)
        
        """
        cdef int buffsize, _file_id
        buffsize = bufsize
        _file_id = self._ncid
        with nogil:
            ierr = ncmpi_buffer_attach(_file_id, buffsize)
        _check_err(ierr)

    def detach_buff(self):
        """
        detach_buff(self)
        
        """
        cdef int _file_id = self._ncid
        with nogil:
            ierr = ncmpi_buffer_detach(_file_id)
        _check_err(ierr)

    def inq_buff_usage(self):
        """
        inq_buff_usage(self)
        
        """
        cdef int _file_id, usage
        _file_id = self._ncid
        with nogil:
            ierr = ncmpi_inq_buffer_usage(_file_id, &usage)
        _check_err(ierr)
        return usage

    def inq_buff_size(self):
        """
        inq_buff_size(self)
        
        """
        cdef int _file_id, buffsize
        _file_id = self._ncid
        with nogil:
            ierr = ncmpi_inq_buffer_size(_file_id, &buffsize)
        _check_err(ierr)
        return buffsize
    
    def inq_unlimdim(self):
        """
        inq_unlimdim(self)

        return the unlimited dim instance of the file"""
        cdef int ierr, unlimdimid
        with nogil:
            ierr = ncmpi_inq_unlimdim(self._ncid, &unlimdimid)
        _check_err(ierr)
        if unlimdimid == -1:
            return None
        for name, dim in self.dimensions.items():
            if dim._dimid == unlimdimid:
                return dim


    def set_fill(self, fillmode):
        """
        set_fill(self, fillmode)

        """
        cdef int _file_id, _fillmode, _old_fillmode
        _file_id = self._ncid
        _fillmode = fillmode
        with nogil:
            ierr = ncmpi_set_fill(_file_id, _fillmode, &_old_fillmode)
        _check_err(ierr)
        return _old_fillmode

    def inq_num_rec_vars(self):
        """
        inq_num_rec_vars(self)

        """
        cdef int ierr, num_rec_vars
        with nogil:
            ierr = ncmpi_inq_num_rec_vars(self._ncid, &num_rec_vars)
        _check_err(ierr)
        return num_rec_vars

    def inq_num_fix_vars(self):
        """
        inq_num_fix_vars(self)

        """
        cdef int ierr, num_fix_vars
        with nogil:
            ierr = ncmpi_inq_num_fix_vars(self._ncid, &num_fix_vars)
        _check_err(ierr)
        return num_fix_vars

    def inq_striping(self):
        """
        inq_striping(self)

        """
        cdef int ierr, striping_size, striping_count
        with nogil:
            ierr = ncmpi_inq_striping(self._ncid, &striping_size, &striping_count)
        _check_err(ierr)
        return striping_size, striping_count

    def inq_recsize(self):
        """
        inq_recsize(self)

        """
        cdef int ierr, recsize
        with nogil:
            ierr = ncmpi_inq_recsize(self._ncid, &recsize)
        _check_err(ierr)
        return recsize

    def inq_version(self):
        """
        inq_version(self)

        """
        cdef int ierr, nc_mode
        with nogil:
            ierr = ncmpi_inq_version(self._ncid, &nc_mode)
        _check_err(ierr)
        return nc_mode


    def inq_info(self):
        """
        inq_info(self)

        """
        cdef MPI_Info *mpiinfo
        cdef int ierr
        cdef Info info_py
        info_py = MPI.Info.Create()
        with nogil:
            ierr = ncmpi_inq_file_info(self._ncid, &info_py.ob_mpi)
        _check_err(ierr)
        return info_py

    def inq_header_size(self):
        """
        inq_header_size(self)

        """
        cdef int ierr
        cdef int size
        with nogil:
            ierr = ncmpi_inq_header_size(self._ncid, <MPI_Offset *>&size)
        _check_err(ierr)
        return size

    def inq_put_size(self):
        """
        inq_put_size(self)

        """
        cdef int ierr
        cdef int size
        with nogil:
            ierr = ncmpi_inq_put_size(self._ncid, <MPI_Offset *>&size)
        _check_err(ierr)
        return size

    def inq_header_extent(self):
        """
        inq_header_extent(self)

        """
        cdef int ierr
        cdef int extent
        with nogil:
            ierr = ncmpi_inq_header_extent(self._ncid, <MPI_Offset *>&extent)
        _check_err(ierr)
        return extent
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

cdef _get_variables(file):
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