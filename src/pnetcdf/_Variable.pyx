###############################################################################
#
#  Copyright (C) 2024, Northwestern University and Argonne National Laboratory
#  See COPYRIGHT notice in top-level directory.
#
###############################################################################

import sys
import os
import subprocess
import numpy as np
import warnings
include "PnetCDF.pxi"

cimport mpi4py.MPI as MPI
from mpi4py.libmpi cimport MPI_Comm, MPI_Info, MPI_Comm_dup, MPI_Info_dup, \
                               MPI_Comm_free, MPI_Info_free, MPI_INFO_NULL,\
                               MPI_COMM_WORLD, MPI_Offset, MPI_DATATYPE_NULL
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy, memset
from ._Dimension cimport Dimension
from ._utils cimport _strencode, _check_err, _set_att, _get_att, _get_att_names, _tostr, _safecast, stringtochar
from ._utils import chartostring
from ._utils cimport _nptonctype, _notcdf2dtypes, _nctonptype, _nptompitype, _supportedtypes, _supportedtypescdf2, \
                     default_fillvals, _StartCountStride, _out_array_shape, _private_atts

cimport numpy
numpy.import_array()




cdef class Variable:
    """
    A PnetCDF variable is used to read and write netCDF data.  They are
    analogous to numpy arrays. See :meth:`Variable.__init__` for more details.

    .. note:: ``Variable`` instances should be created using the
        :meth:`File.def_var` method of a :meth:`File` instance, not using this
        class constructor directly.
    """

    def __init__(self, file, name, datatype, dimensions=(), fill_value=None, **kwargs):
        """
        __init__(self, file, name, datatype, dimensions=(), fill_value=None, **kwargs)

        The constructor for :class:`pnetcdf.Variable`.

        :param str varname: Name of the new variable.

        :param datatype: The data type of the new variable.
            It can be a string that describes a numpy dtype object, a numpy
            dtype object, or one of PnetCDF data type constant, as shown below.

            - ``pnetcdf.NC_CHAR`` or ``S1`` for 1-character string
            - ``pnetcdf.NC_BYTE`` or ``i1`` for 1-byte integer
            - ``pnetcdf.NC_SHORT`` or ``i2`` for 2-byte signed integer
            - ``pnetcdf.NC_INT`` or ``i4`` for 4-byte signed integer
            - ``pnetcdf.NC_FLOAT`` or ``f4`` for 4-byte floating point number
            - ``pnetcdf.NC_DOUBLE`` or ``f8`` for 8-byte real number in double precision

            The following additional data types are available for `CDF-5` format.

            - ``pnetcdf.NC_UBYTE`` or ``u1`` for unsigned 1-byte integer
            - ``pnetcdf.NC_USHORT`` or ``u2`` for unsigned 2-byte integer
            - ``pnetcdf.NC_UINT`` or ``u4`` for unsigned 4-byte integer
            - ``pnetcdf.NC_INT64`` or ``i8`` for signed 8-byte integer
            - ``pnetcdf.NC_UINT64`` or ``u8`` for unsigned 8-byte integer

        :param dimensions: [Optional]
            The dimensions of the new variable. Can be either dimension names
            or dimension class instances. Default is an empty tuple which means
            the variable is a scalar (and therefore has no dimensions).
        :type dimensions: tuple of str or :class:`pnetcdf.Dimension` instances

        :param fill_value: [Optional] The fill value of the new variable.
            Accepted values are shown below.

            - ``None`` to use the default netCDF fill value for the given data type.
            - ``False`` to turn off the fill mode.
            - If specified with other value, the default netCDF `_FillValue`
              (the value that the variable gets filled with before any data is
              written to it) is replaced with this value.

        :return: The created variable
        :rtype: :class:`pnetcdf.Variable`

        :Example: A example is available in ``examples/put_var.py``

         ::

           # Define dimensions
           dim_y = f.def_dim("Y", global_ny)
           dim_x = f.def_dim("X", global_nx)

           # Define a 2D variable of integer type, using :meth:`File.def_var`.
           var = f.def_var("var", pnetcdf.NC_INT, (dim_y, dim_x))

           # Or equivalently, using :meth:`File.createVariable`.
           var = f.createVariable("var", pnetcdf.NC_INT, (dim_y, dim_x))

        """

        cdef int ierr, ndims, icontiguous, icomplevel, numdims, _file_id, nsd,
        cdef char namstring[NC_MAX_NAME+1]
        cdef char *varname
        cdef nc_type xtype
        cdef int *dimids
        cdef size_t sizep, nelemsp
        cdef size_t *chunksizesp
        cdef float preemptionp
        self._file_id = file._ncid

        self._file = file
        _file_id = self._file_id
        #TODO: decide whether we need to check xtype at python-level
        if isinstance(datatype, str): # convert to numpy data type object
            datatype = np.dtype(datatype)
        if isinstance(datatype, np.dtype):
            if datatype.str[1:] in _supportedtypes:
                xtype = _nptonctype[datatype.str[1:]]
            else:
                raise TypeError('illegal data type, must be one of %s, got %s' % (_supportedtypes, datatype.str[1:]))
        elif isinstance(datatype, int):
            xtype = datatype
        else:
            raise TypeError('illegal data type, must be an int, got %s' % (datatype.str[1:]))
        self.xtype = xtype
        self.dtype = np.dtype(_nctonptype[xtype])

        if 'id' in kwargs:
            self._varid = kwargs['id']
        else:
            bytestr = _strencode(name)
            varname = bytestr
            ndims = len(dimensions)
            # find dimension ids.
            if ndims:
                dimids = <int *>malloc(sizeof(int) * ndims)
                for n from 0 <= n < ndims:
                    dimids[n] = dimensions[n]._dimid
            if ndims:
                with nogil:
                    ierr = ncmpi_def_var(_file_id, varname, xtype, ndims,
                                    dimids, &self._varid)
                free(dimids)
            else: # a scalar variable.
                with nogil:
                    ierr = ncmpi_def_var(_file_id, varname, xtype, ndims,
                                    NULL, &self._varid)
            if ierr != NC_NOERR:
                _check_err(ierr)

        # count how many unlimited dimensions there are.
        self._nunlimdim = 0
        for dim in dimensions:
            if dim.isunlimited(): self._nunlimdim = self._nunlimdim + 1
        # set ndim attribute (number of dimensions).
        with nogil:
            ierr = ncmpi_inq_varndims(_file_id, self._varid, &numdims)
        _check_err(ierr)
        self.ndim = numdims
        self._name = name

        # default is to automatically convert to/from character
        # to string arrays when _Encoding variable attribute is set.
        self.chartostring = True
        # propagate _ncstring_attrs__ setting from parent group.

        if fill_value != None:
            self.def_fill(0, fill_value = fill_value)


    def __array__(self):
        # numpy special method that returns a numpy array.
        # This allows numpy Universal functions ufuncs to work faster on
        # Variable instances.
        return self[...]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        cdef int ierr, no_fill
        ncdump = [repr(type(self))]
        show_more_dtype = True
        kind = str(self.dtype)
        dimnames = tuple(_tostr(dimname) for dimname in self.dimensions)
        ncdump.append('%s %s(%s)' %\
            (kind, self._name, ', '.join(dimnames)))
        for name in self.ncattrs():
            ncdump.append('    %s: %s' % (name, self.get_att(name)))
        if show_more_dtype:
            ncdump.append('%s data type: %s' % (kind, self.dtype))
        unlimdims = []
        for dimname in self.dimensions:
            dim = self._file.dimensions[dimname]
            if dim.isunlimited():
                unlimdims.append(dimname)

        ncdump.append('unlimited dimensions: %s' % ', '.join(unlimdims))
        ncdump.append('current shape = %r' % (self.shape,))

        with nogil:
            ierr = ncmpi_inq_var_fill(self._file_id,self._varid,&no_fill,NULL)
        _check_err(ierr)

        if no_fill != 1:
            try:
                fillval = self._FillValue
                msg = 'filling on'
            except AttributeError:
                fillval = default_fillvals[self.dtype.str[1:]]
                if self.dtype.str[1:] in ['u1','i1']:
                    msg = 'filling on, default _FillValue of %s ignored' % fillval
                else:
                    msg = 'filling on, default _FillValue of %s used' % fillval
            ncdump.append(msg)
        else:
            ncdump.append('filling off')
        return '\n'.join(ncdump)

    def _getdims(self):
        # Private method to get variable's dimension names
        cdef int ierr, numdims, n, nn
        cdef char namstring[NC_MAX_NAME+1]
        cdef int *dimids
        # get number of dimensions for this variable.
        with nogil:
            ierr = ncmpi_inq_varndims(self._file_id, self._varid, &numdims)
        _check_err(ierr)
        dimids = <int *>malloc(sizeof(int) * numdims)
        # get dimension ids.
        with nogil:
            ierr = ncmpi_inq_vardimid(self._file_id, self._varid, dimids)
        _check_err(ierr)
        # loop over dimensions, retrieve names.
        dimensions = ()
        for nn from 0 <= nn < numdims:
            with nogil:
                ierr = ncmpi_inq_dimname(self._file_id, dimids[nn], namstring)
            _check_err(ierr)
            name = namstring.decode('utf-8')
            dimensions = dimensions + (name,)
        free(dimids)
        return dimensions

    def _getname(self):
        # Private method to get name associated with instance
        cdef int err, _file_id
        cdef char namstring[NC_MAX_NAME+1]
        _file_id = self._file._ncid
        with nogil:
            ierr = ncmpi_inq_varname(_file_id, self._varid, namstring)
        _check_err(ierr)
        return namstring.decode('utf-8')

    property name:
        """string name of Variable instance"""
        def __get__(self):
            return self._getname()
        def __set__(self,value):
            raise AttributeError("name cannot be altered")

    property datatype:
        """Return the mapped numpy data type of the variable netCDF datatype """
        def __get__(self):
            return self.dtype

    property shape:
        """Find current sizes of all variable dimensions"""
        def __get__(self):
            shape = ()
            for dimname in self._getdims():
                # look in current group, and parents for dim.
                dim = self._file.dimensions[dimname]
                shape = shape + (len(dim),)
            return shape
        def __set__(self,value):
            raise AttributeError("shape cannot be altered")

    property size:
        """Return the number of stored elements."""
        def __get__(self):
            return int(np.prod(self.shape))

    property dimensions:
        """Get variable's dimension names"""
        def __get__(self):
            return self._getdims()
        def __set__(self,value):
            raise AttributeError("dimensions cannot be altered")
    def file(self):
        """
        file(self)

        Return the netCDF file instance that the variable is contained in.

        :rtype: :class:`pnetcdf.File`
        """
        return self._file

    def ncattrs(self):
        """
        ncattrs(self)

        :return: all attribute names of this variable in a list.
        :rtype: list
        """
        return _get_att_names(self._file_id, self._varid)

    def put_att(self,name,value):
        """
        put_att(self,name,value)

        Method add or change a variable attribute. If this attribute is new, or
        if the space required to store the attribute is greater than before,
        the netCDF file must be in define mode.

        :param name: Name of the attribute.
        :type name: str

        :param value: Value of the attribute.
        :type value: str or numpy.ndarray

        :Operational mode: This method must be called while the associated
            netCDF file is in define mode.

        :Example: A example is available in ``examples/put_var.py``

         ::

           str_att = "example attribute of type text."
           var.put_att("foo_attr", str_att)

           # Equivalently, uses python dictionary way
           var.foo_attr = str_att

        """
        cdef nc_type xtype
        xtype=-99
        _set_att(self._file, self._varid, name, value, xtype=xtype)


    def get_att(self,name,encoding='utf-8'):
        """
        get_att(self,name,encoding='utf-8')

        Retrieve an attribute of a netCDF variable.

        :param name: Name of the attribute.
        :type name: str

        :param encoding: specify the character encoding of a string attribute
            (default is `utf-8`).
        :type name: str

        :rtype: str or numpy.ndarray

        :Operational mode: This method can be called while the file is in either
            define or data mode (collective or independent).

        :Example: A example is available in ``examples/get_var.py``

         ::

           # Get attribute named "foo_attr"
           str_att = v.get_att("foo_attr")

           # Equivalently, uses python dictionary way
           str_att = v.foo_attr

        """
        return _get_att(self._file, self._varid, name, encoding=encoding)

    def del_att(self, name):
        """
        del_att(self,name,value)

        Delete a netCDF variable attribute.

        :param name: Name of the attribute
        :type name: str

        :Operational mode: This method must be called while the associated
            netCDF file is in define mode.
        """
        cdef char *attname
        bytestr = _strencode(name)
        attname = bytestr
        with nogil:
            ierr = ncmpi_del_att(self._file_id, self._varid, attname)
        _check_err(ierr)

    def __delattr__(self,name):
        # if it's a netCDF attribute, remove it
        if name not in _private_atts:
            self.del_att(name)
        else:
            raise AttributeError(
            "'%s' is one of the reserved attributes %s, cannot delete. Use del_att instead." % (name, tuple(_private_atts)))

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
                    values.append(_get_att(self._file, self._varid, name))
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

        Rename a variable attribute named `oldname` to `newname`

        :param oldname: Old name of the attribute.
        :type oldname: str

        :Operational mode: If the new name is longer than the original name, the
            associated netCDF file must be in define mode.  Otherwise, the
            netCDF file can be in either define or data mode.
        """
        cdef char *oldnamec
        cdef char *newnamec
        cdef int ierr
        bytestr = _strencode(oldname)
        oldnamec = bytestr
        bytestr = _strencode(newname)
        newnamec = bytestr
        with nogil:
            ierr = ncmpi_rename_att(self._file_id, self._varid, oldnamec, newnamec)
        _check_err(ierr)

    def get_dims(self):
        """
        get_dims(self)

        :return: a tuple of ``Dimension`` instances associated with this
            variable.
        :rtype: tuple of ``Dimension``
        """
        return tuple(self._file.dimensions[dim] for dim in self.dimensions)

    def def_fill(self, int no_fill, fill_value = None):
        """
        def_fill(self, int no_fill, fill_value = None)

        Sets the fill mode for a variable. This API must be called while the
        file is in the define mode, and after the variable is defined.

        :param no_fill: Set no_fill mode for a variable. 1 for on (not to fill)
            and 0 for off (to fill).
        :type no_fill: int

        :param fill_value: Sets the customized fill value. Must be the same
            type as the variable. This will be written to a `_FillValue`
            attribute, created for this purpose. If None, this argument will be
            ignored and the default fill value is used.
        :type fill_value: any

        :Example: A example is available in ``examples/fill_mode.py``

         ::

           # set the variable's fill mode to NC_FILL with PnetCDF default fill value
           var.def_fill(no_fill = 0)

           # enable the variable's fill mode and use a customized value
           fill_value = np.int32(-1)
           var.def_fill(no_fill = 0, fill_value = fill_value)

           # Equivalently this can be done by setting the PnetCDF pre-defined attribute "_FillValue"
           var._FillValue = fill_value

        """
        cdef ndarray data
        cdef int ierr, _no_fill
        _no_fill = no_fill
        if fill_value is None:
            with nogil:
                ierr = ncmpi_def_var_fill(self._file_id, self._varid, _no_fill, NULL)
        else:
            data = np.array(fill_value)
            with nogil:
                ierr = ncmpi_def_var_fill(self._file_id, self._varid, _no_fill, PyArray_DATA(data))
        _check_err(ierr)

    def inq_fill(self):
        """
        inq_fill(self)

        Returns the fill mode settings of this variable. A tuple of two values
        representing no_fill mode and fill value.

        :return: A tuple of two values which are ``no_fill`` mode and
            ``fill_value``, respectively.

             - ``no_fill``: 1 if no_fill mode is set (else 0).
             - ``fill_value``: the fill value for this variable.

        :rtype: tuple
        """

        cdef int ierr, no_fill
        cdef ndarray fill_value
        fill_value = np.empty((1,), self.dtype)
        with nogil:
            ierr = ncmpi_inq_var_fill(self._file_id, self._varid, &no_fill, PyArray_DATA(fill_value))
        _check_err(ierr)

        return no_fill, fill_value[0]

    def fill_rec(self, int rec_no):
        """
        fill_rec(self, int rec_no)

        Fills a record of a record variable with predefined or user-defined
        fill values.

        :param rec_no: the index of the record to be filled
        :type rec_no: int
        """
        cdef int recno, ierr
        recno = rec_no
        with nogil:
            ierr = ncmpi_fill_var_rec(self._file_id, self._varid, recno)
        _check_err(ierr)

    def set_auto_chartostring(self,chartostring):
        """
        set_auto_chartostring(self,chartostring)

        Turn on or off automatic conversion of character variable data to and
        from numpy fixed length string arrays when the `_Encoding` variable attribute
        is set.

        If `chartostring` is set to `True`, when data is read from a character
        variable (dtype = `S1`) that has an `_Encoding` attribute, it is
        converted to a numpy fixed length unicode string array (dtype = `UN`,
        where `N` is the length of the rightmost dimension of the variable).
        The value of `_Encoding` is the unicode encoding that is used to decode
        the bytes into strings.

        When numpy string data is written to a variable it is converted back to
        indiviual bytes, with the number of bytes in each string equalling the
        rightmost dimension of the variable.

        The default value of `chartostring` is `True`
        (automatic conversions are performed).
        """
        self.chartostring = bool(chartostring)

    def __getitem__(self, elem):
        # This special method is used to index the netCDF variable using the
        # "extended slice syntax". The extended slice syntax is a perfect match
        # for the "start", "count" and "stride" arguments to the C function
        # ncmpi_get_var(), and is much more easy to use.
        start, count, stride, put_ind =\
        _StartCountStride(elem,self.shape,dimensions=self.dimensions,file=self._file)
        datashape = _out_array_shape(count)
        data = np.empty(datashape, dtype=self.dtype)

        # Determine which dimensions need to be
        # squeezed (those for which elem is an integer scalar).
        # The convention used is that for those cases,
        # put_ind for this dimension is set to -1 by _StartCountStride.
        squeeze = data.ndim * [slice(None),]
        for i,n in enumerate(put_ind.shape[:-1]):
            if n == 1 and put_ind.size > 0 and put_ind[...,i].ravel()[0] == -1:
                squeeze[i] = 0

        # Reshape the arrays so we can iterate over them.
        start = start.reshape((-1, self.ndim or 1))
        count = count.reshape((-1, self.ndim or 1))
        stride = stride.reshape((-1, self.ndim or 1))
        put_ind = put_ind.reshape((-1, self.ndim or 1))

        # Fill output array with data chunks.
        for (a,b,c,i) in zip(start, count, stride, put_ind):
            datout = self._get(a,b,c)
            if not hasattr(datout,'shape') or data.shape == datout.shape:
                data = datout
            else:
                shape = getattr(data[tuple(i)], 'shape', ())
                if not len(self.dimensions):
                    # special case of scalar VLEN
                    data[0] = datout
                else:
                    data[tuple(i)] = datout.reshape(shape)

        # Remove extra singleton dimensions.
        if hasattr(data,'shape'):
            data = data[tuple(squeeze)]
        if hasattr(data,'ndim') and self.ndim == 0:
            # Make sure a numpy scalar array is returned instead of a 1-d array of
            # length 1.
            if data.ndim != 0: data = np.asarray(data[0])

        # if _Encoding is specified for a character variable, return
        # a numpy array of strings with one less dimension.
        if self.chartostring and getattr(self.dtype,'kind',None) == 'S' and\
           getattr(self.dtype,'itemsize',None) == 1:
            encoding = getattr(self,'_Encoding',None)
            # should there be some other way to disable this?
            if encoding is not None:
                # only try to return a string array if rightmost dimension of
                # sliced data matches rightmost dimension of char variable
                if len(data.shape) > 0 and data.shape[-1] == self.shape[-1]:
                    # also make sure slice is along last dimension
                    matchdim = True
                    for cnt in count:
                        if cnt[-1] != self.shape[-1]:
                            matchdim = False
                            break
                    if matchdim:
                        data = chartostring(data, encoding=encoding)
        return data

    def __setitem__(self, elem, data):
        # This special method is used to assign to the netCDF variable using
        # "extended slice syntax". The extended slice syntax is a perfect match
        # for the "start", "count" and "stride" arguments to the C function
        # ncmpi_put_var(), and is much more easy to use.

        # if _Encoding is specified for a character variable, convert
        # numpy array of strings to a numpy array of characters with one more
        # dimension.
        if self.chartostring and getattr(self.dtype,'kind',None) == 'S' and\
           getattr(self.dtype,'itemsize',None) == 1:
            # NC_CHAR variable
            encoding = getattr(self,'_Encoding',None)
            if encoding is not None:
                # _Encoding attribute is set
                # if data is a string or a bytes object, convert to a numpy string array
                # whose length is equal to the rightmost dimension of the
                # variable.
                if type(data) in [str,bytes]: data = np.asarray(data,dtype='S'+repr(self.shape[-1]))
                if data.dtype.kind in ['S','U'] and data.dtype.itemsize > 1:
                    # if data is a numpy string array, convert it to an array
                    # of characters with one more dimension.
                    data = stringtochar(data, encoding=encoding)

        start, count, stride, put_ind =\
        _StartCountStride(elem,self.shape,self.dimensions,self._file,datashape=data.shape,put=True)
        datashape = _out_array_shape(count)

        # if a numpy scalar, create an array of the right size
        # and fill with scalar values.
        if data.shape == ():
            data = np.tile(data,datashape)
        # reshape data array if needed to conform with start,count,stride.
        if data.ndim != len(datashape) or\
           (data.shape != datashape and data.ndim > 1): 
            # create a view so shape in caller is not modified
            try: # if extra singleton dims, just reshape
                data = data.view()
                data.shape = tuple(datashape)
            except ValueError: # otherwise broadcast
                data = np.broadcast_to(data, datashape)

        # Reshape these arrays so we can iterate over them.
        start = start.reshape((-1, self.ndim or 1))
        count = count.reshape((-1, self.ndim or 1))
        stride = stride.reshape((-1, self.ndim or 1))
        put_ind = put_ind.reshape((-1, self.ndim or 1))

        # Fill output array with data chunks.
        for (a,b,c,i) in zip(start, count, stride, put_ind):
            dataput = data[tuple(i)]
            if dataput.size == 0: continue # nothing to write
            # convert array scalar to regular array with one element.
            if dataput.shape == ():
                dataput=np.array(dataput,dataput.dtype)
            self._put(dataput,a,b,c)


    def _put_var1(self, value, tuple index, bufcount, MPI.Datatype buftype, collective = True):
        cdef int ierr, ndims
        cdef size_t *indexp
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef ndarray data
        # rank of variable.
        data = np.array(value)
        ndim_index = len(index)
        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        indexp = <size_t *>malloc(sizeof(size_t) * ndim_index)
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        for i, val in enumerate(index):
            indexp[i] = val
        if data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if collective:
            with nogil:
                ierr = ncmpi_put_var1_all(self._file_id, self._varid, \
                                    <const MPI_Offset *>indexp, PyArray_DATA(data), buffcount, bufftype)
        else:
            with nogil:
                ierr = ncmpi_put_var1(self._file_id, self._varid, \
                                    <const MPI_Offset *>indexp, PyArray_DATA(data), buffcount, bufftype)
        _check_err(ierr)
        free(indexp)

    def _put_var(self, ndarray data, bufcount, MPI.Datatype buftype, collective = True):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        #data = data.flatten()
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        #bufcount = data.size
        if data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        #bufftype = MPI_DATATYPE_NULL
        if collective:
            with nogil:
                ierr = ncmpi_put_var_all(self._file_id, self._varid, \
                                     PyArray_DATA(data), buffcount, bufftype)
        else:
            with nogil:
                ierr = ncmpi_put_var(self._file_id, self._varid, \
                                     PyArray_DATA(data), buffcount, bufftype)
        _check_err(ierr)

    def _put_vara(self, start, count, ndarray data, bufcount, MPI.Datatype buftype, collective = True):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t *startp
        cdef size_t *countp
        ndims = len(self.dimensions)
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        for n from 0 <= n < ndims:
            countp[n] = count[n]
            startp[n] = start[n]
        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        #data = data.flatten()
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        #bufcount = data.size
        if data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if collective:
            with nogil:
                ierr = ncmpi_put_vara_all(self._file_id, self._varid, <const MPI_Offset *>startp, <const MPI_Offset *>countp,\
                                     PyArray_DATA(data), buffcount, bufftype)
        else:
            with nogil:
                ierr = ncmpi_put_vara(self._file_id, self._varid, <const MPI_Offset *>startp, <const MPI_Offset *>countp,\
                                     PyArray_DATA(data), buffcount, bufftype)
        _check_err(ierr)

    def _put_varn(self, ndarray data, num, starts, counts=None, bufcount=None, MPI.Datatype buftype=None, collective = True):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t **startsp
        cdef size_t **countsp
        cdef int num_req
        num_req = num
        ndims = len(self.dimensions)
        max_num_req = len(starts)

        startsp = <size_t**> malloc(max_num_req * sizeof(size_t*));
        for i in range(max_num_req):
            startsp[i] = <size_t*> malloc(ndims * sizeof(size_t));
            for j in range(ndims):
                startsp[i][j] = starts[i, j]

        countsp = <size_t**> malloc(max_num_req * sizeof(size_t*));
        for i in range(max_num_req):
            countsp[i] = <size_t*> malloc(ndims * sizeof(size_t));
            for j in range(ndims):
                countsp[i][j] = counts[i, j]

        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        #data = data.flatten()
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        #bufcount = data.size
        if data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if collective:
            with nogil:
                ierr = ncmpi_put_varn_all(self._file_id,
                                          self._varid,
                                          num_req,
                                          <const MPI_Offset **>startsp,
                                          <const MPI_Offset **>countsp,
                                          PyArray_DATA(data),
                                          buffcount,
                                          bufftype)
        else:
            with nogil:
                ierr = ncmpi_put_varn(self._file_id,
                                      self._varid,
                                      num_req,
                                      <const MPI_Offset **>startsp,
                                      <const MPI_Offset **>countsp,
                                      PyArray_DATA(data),
                                      buffcount,
                                      bufftype)
        _check_err(ierr)

    def put_varn_all(self, data, num, starts, counts=None, bufcount=None, MPI.Datatype buftype=None):
        """
        put_varn_all(self, data, num, starts, counts=None, bufcount=None, buftype=None)

        Method write multiple subarrays of a netCDF variable to the file.  This
        an collective I/O call and can only be called when the file is in the
        collective I/O mode. This method is equivalent to making multiple
        calls to :meth:`Variable.put_var`. Note, combining multiple `put_var`
        calls into one can achieve a better performance.

        - `data`, `num`, `starts`, `counts` -  Write multiple subarrays of values.
           The part of the netCDF variable to write is specified by giving
           multiple subarrays and each subarray is specified by a corner and a
           vector of edge lengths that refer to an array section of the netCDF
           variable.  The example code and diagram below illustrates a 4
           subarray section in a 4 * 10 two-dimensional variable ("-" means
           skip).

           ::

            num = 4

            starts[0][0] = 0; starts[0][1] = 5; counts[0][0] = 1; counts[0][1] = 2
            starts[1][0] = 1; starts[1][1] = 0; counts[1][0] = 1; counts[1][1] = 1
            starts[2][0] = 2; starts[2][1] = 6; counts[2][0] = 1; counts[2][1] = 2
            starts[3][0] = 3; starts[3][1] = 0; counts[3][0] = 1; counts[3][1] = 3

                                 -  -  -  -  -  a  b  -  -  -
            a b c d e f g h  ->  c  -  -  -  -  -  -  -  -  -
                                 -  -  -  -  -  -  d  e  -  -
                                 f  g  h  -  -  -  -  -  -  -

        :param data: the numpy array that stores array values to be written,
            which serves as a write buffer. When writing a single data value,
            it can also be a single numeric (e.g. np.int32) python variable.
            The datatype should match with the variable's datatype. Note this
            numpy array write buffer can be in any shape as long as the number
            of elements (buffer size) is matched. If the in-memory type of data
            values differs from the netCDF variable type defined in the file,
            type conversion will automatically be applied.
        :type data: numpy.ndarray

        :param num: An integer specifying the number of subarrays.
        :type num: int

        :param starts:
            A 2D array of integers containing starting array indices
            of `num` number of subarrays.  The first dimension of `starts`
            should be of size `num`, indicating the number of subarrays of the
            variable to be written. The second dimension is of size equal to
            the number dimensions of the variable.  For example, when `num` = 3
            and the variable defined in the file is a 2D array, `starts` should
            be a 3x2 array.  Each of the subarray starting indices identify
            the indices in the variable where the first of the data values will
            be written. Each `starts[i]` is a vector specifying the index in
            the variable where the first of the data values will be written.
            The elements of `starts[i][*]` must correspond to the variable’s
            dimensions in order.  Hence, if the variable is a record variable,
            the first index, `starts[i][0]` would correspond to the starting
            record number for writing the data values.
        :type starts: numpy.ndarray

        :param counts: [Optional]
            A 2D array of integers specifying the lengths along each
            dimension of `num` number of subarrays to be written. The first
            dimension of `counts` should be of size `num`, indicating the
            number of subarrays of the variable to be written. The second
            dimension is of size equal to the number dimensions of the
            variable.  For example, when `num` = 3 and the variable defined in
            the file is a 2D array, `counts` should be a 3x2 array.  Each of
            the subarray `counts[i]` is a vector specifying the lengths along
            each dimension of the block of data values to be written and must
            correspond to the variable’s dimensions in order.  When this
            argument is not supplied, it is equivalent to providing counts of
            all 1s.
        :type counts: numpy.ndarray

        :param bufcount: [Optional]
            An integer indicates the number of MPI derived data type elements
            in the write buffer to be written to the file.
        :type bufcount: int

        :param buftype: [Optional]
            An MPI derived data type that describes the memory layout of the
            write buffer.
        :type buftype: mpi4py.MPI.Datatype

        :Example: A example is available in ``examples/put_varn_int.py``

         ::

           num_reqs = 4
           starts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
           counts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
           starts[0][0] = 0; starts[0][1] = 5; counts[0][0] = 1; counts[0][1] = 2
           starts[1][0] = 1; starts[1][1] = 0; counts[1][0] = 1; counts[1][1] = 1
           starts[2][0] = 2; starts[2][1] = 6; counts[2][0] = 1; counts[2][1] = 2
           starts[3][0] = 3; starts[3][1] = 0; counts[3][0] = 1; counts[3][1] = 3

           v.put_varn_all(w_buf, num = num_reqs, starts = starts, counts = counts)

        """
        self._put_varn(data, num, starts, counts, bufcount = bufcount,
                       buftype = buftype, collective = True)

    def put_varn(self, data, num, starts, counts=None, bufcount=None, MPI.Datatype buftype=None):
        """
        put_varn(self, data, num, starts, counts=None, bufcount=None, buftype=None)

        This method call is the same as method :meth:`Variable.put_varn_all`,
        except it is an independent call and can only be called in the
        independent I/O mode. Please refer to :meth:`Variable.put_varn_all` for
        its argument usage.
        """
        self._put_varn(data, num, starts, counts, bufcount = bufcount,
                       buftype = buftype, collective = False)

    def iput_varn(self, data, num, starts, counts=None, bufcount=None, MPI.Datatype buftype=None):
        """
        iput_varn(self, data, num, starts, counts=None, bufcount=None, buftype=None)

        This method call is the nonblocking counterpart of
        :meth:`Variable.put_varn`. The syntax is the same as
        :meth:`Variable.put_varn`. For the argument usage, please refer to
        method :meth:`Variable.put_varn_all`. This method returns a request ID
        that can be used in :meth:`File.wait_all` or :meth:`File.wait`. The
        posted write request may not be committed until :meth:`File.wait_all` or
        :meth:`File.wait` is called.

        .. note::
            Unlike :meth:`Variable.put_varn`, the posted nonblocking write
            requests may not be committed to the file until the time of calling
            :meth:`File.wait_all` or :meth:`File.wait`.  Users should not
            alter the contents of the write buffer once the request is posted
            until the :meth:`File.wait_all` or :meth:`File.wait` is
            returned. Any change to the buffer contents in between will result
            in unexpected error.

        :return: The request ID, which can be used in a successive call to
            :meth:`File.wait_all` or :meth:`File.wait` for the completion
            of the nonblocking operation.
        :rtype: int
        """
        return self._iput_varn(data, num, starts, counts, bufcount, buftype,
                               buffered=False)

    def bput_varn(self, data, num, starts, counts=None, bufcount=None, MPI.Datatype buftype=None):
        """
        bput_varn(self, data, num, starts, counts=None, bufcount=None, buftype=None)

        This method call is the nonblocking, buffered counterpart of
        :meth:`Variable.put_varn`. For the argument usage, please refer to
        method :meth:`Variable.put_varn_all`. This method returns a request ID
        that can be used in :meth:`File.wait_all` or :meth:`File.wait`. The
        posted write request may not be committed until :meth:`File.wait_all`
        or :meth:`File.wait` is called.

        .. note::
            Unlike :meth:`Variable.iput_varn`, the write data is buffered
            (cached) internally by PnetCDF and will be flushed to the file at
            the time of calling :meth:`File.wait_all` or :meth:`File.wait`.
            Once the call to this method returns, the caller is free to change
            the contents of write buffer. Prior to calling this method, make
            sure :meth:`File.attach_buff` is called to allocate an internal
            buffer for accommodating the write requests.

        :return: The request ID, which can be used in a successive call to
            :meth:`File.wait_all` or :meth:`File.wait` for the completion
            of the nonblocking operation.
        :rtype: int
        """
        return self._iput_varn(data, num, starts, counts, bufcount, buftype, buffered=True)

    def _put_vars(self, start, count, stride, ndarray data, bufcount, MPI.Datatype buftype, collective = True):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t *startp
        cdef size_t *countp
        cdef ptrdiff_t *stridep
        ndims = len(self.dimensions)
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        stridep = <ptrdiff_t *>malloc(sizeof(ptrdiff_t) * ndims)
        for n from 0 <= n < ndims:
            countp[n] = count[n]
            startp[n] = start[n]
            stridep[n] = stride[n]
        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        #data = data.flatten()
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        #bufcount = data.size
        if data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if collective:
            with nogil:
                ierr = ncmpi_put_vars_all(self._file_id, self._varid, \
                                        <const MPI_Offset *>startp, <const MPI_Offset *>countp, \
                                        <const MPI_Offset *>stridep, PyArray_DATA(data), buffcount, bufftype)
        else:
            with nogil:
                ierr = ncmpi_put_vars(self._file_id, self._varid, \
                                        <const MPI_Offset *>startp, <const MPI_Offset *>countp, \
                                        <const MPI_Offset *>stridep, PyArray_DATA(data), buffcount, bufftype)
        _check_err(ierr)


    def _put_varm(self, ndarray data, start, count, stride, imap, bufcount, MPI.Datatype buftype, collective = True):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t *startp
        cdef size_t *countp
        cdef ptrdiff_t *stridep
        cdef size_t *imapp
        ndims = len(self.dimensions)
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        stridep = <ptrdiff_t *>malloc(sizeof(ptrdiff_t) * ndims)
        imapp = <size_t *>malloc(sizeof(size_t) * ndims)
        for n from 0 <= n < ndims:
            countp[n] = count[n]
            startp[n] = start[n]
            if stride is not None:
                stridep[n] = stride[n]
            else:
                stridep[n] = 1
            imapp[n] = imap[n]

        shapeout = ()
        for lendim in count:
            shapeout = shapeout + (lendim,)
        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        if data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if collective:
            with nogil:
                ierr = ncmpi_put_varm_all(self._file_id, self._varid, <const MPI_Offset *>startp, \
                                        <const MPI_Offset *>countp, <const MPI_Offset *>stridep, \
                                        <const MPI_Offset *>imapp, PyArray_DATA(data), buffcount, bufftype)
        else:
            with nogil:
                ierr = ncmpi_put_varm(self._file_id, self._varid, <const MPI_Offset *>startp, \
                                        <const MPI_Offset *>countp, <const MPI_Offset *>stridep, \
                                        <const MPI_Offset *>imapp, PyArray_DATA(data), buffcount, bufftype)
        _check_err(ierr)




    def put_var_all(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, MPI.Datatype buftype=None):
        """
        put_var_all(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None)

        Method to write in parallel to the netCDF variable in the collective
        I/O mode. The behavior of the method varies depends on the pattern of
        provided optional arguments - `start`, `count`, `stride`, `bufcount`
        and `buftype`.

        - `data` - Write an entire variable.
           Write a netCDF variable entirely of an opened netCDF file, i.e.
           calling this API with only argument `data`. This is the simplest
           interface to use for writing a value in a scalar variable or
           whenever all the values of a multidimensional variable can all be
           written at once.

           .. note:: Be careful when using the simplest forms of this interface
              with record variables. When there is no record written into the
              file yet, calling this API with only argument `data`, nothing
              will be written. Similarly, when writing the entire record
              variable, one must take the number of records into account.

        - `data`, `start` - Write a single data value (a single element).
           Put a single data value specified by `start` into a variable of an
           opened netCDF file. For example, start = [0,5] would specify the
           following position in a 4 * 10 two-dimensional variable ("-" means
           skip).

           ::

                       -  -  -  -  -  a  -  -  -  -
            a     ->   -  -  -  -  -  -  -  -  -  -
                       -  -  -  -  -  -  -  -  -  -
                       -  -  -  -  -  -  -  -  -  -

        - `data`, `start`, `count` - Write a subarray of values.
           The part of the netCDF variable to write is specified by giving a
           corner index and a vector of edge lengths that refer to an array
           section of the netCDF variable. For example, start = [0,5] and count
           = [2,2] would specify the following array section in a 4 * 10
           two-dimensional variable ("-" means skip).

           ::

                        -  -  -  -  -  a  b  -  -  -
            a  b   ->   -  -  -  -  -  c  d  -  -  -
            c  d        -  -  -  -  -  -  -  -  -  -
                        -  -  -  -  -  -  -  -  -  -

        - `data`, `start`, `count`, `stride` - Write a subarray of values with strided space.
           The part of the netCDF variable to write is specified by giving a
           corner, a vector of edge lengths and stride vector that refer to a
           subsampled array section of the netCDF variable. For example, start
           = [0,2], count = [2,4] and stride = [1,2] would specify the
           following array section in a 4 * 10 two-dimensional variable ("-"
           means skip).

           ::

                             -  -  a  -  b  -  c  -  d  -
            a  b  c  d   ->  -  -  e  -  f  -  g  -  h  -
            e  f  g  h       -  -  -  -  -  -  -  -  -  -
                             -  -  -  -  -  -  -  -  -  -

        - `data`, `start`, `count`, `stride`, `imap` - Write a mapped array of values.
           The mapped array section is specified by giving a corner, a vector
           of counts, a stride vector, and an index mapping vector.  The index
           mapping vector (imap) is a vector of integers that specifies the
           mapping between the dimensions of a netCDF variable and the
           in-memory structure of the internal data array. For example, imap =
           [3,8], start = [0,5] and count = [2,2] would specify the following
           section in write butter and array section in a 4 * 10
           two-dimensional variable ("-" means skip).

           ::

                                       -  -  -  -  -  a  c  -  -  -
            a - - b         a  c       -  -  -  -  -  b  d  -  -  -
            - - - -    ->   b  d  ->   -  -  -  -  -  -  -  -  -  -
            c - - d                    -  -  -  -  -  -  -  -  -  -

            distance from a to b is 3 in buffer => imap[0] = 3
            distance from a to c is 8 in buffer => imap[1] = 8

        :param data: the numpy array that stores array values to be written,
            which serves as a write buffer. When writing a single data value,
            it can also be a single numeric (e.g. np.int32) python variable.
            The datatype should match with the variable's datatype. Note this
            numpy array write buffer can be in any shape as long as the number
            of elements (buffer size) is matched.
        :type data: numpy.ndarray

        :param start: [Optional]
            Only relevant when writing a array of values, a subsampled array, a
            mapped array or a list of subarrays.  An array of integers
            specifying the index in the variable where the first of the data
            values will be written. The elements of `start` must correspond to
            the variable’s dimensions in order. Hence, if the variable is a
            record variable, the first index would correspond to the starting
            record number for writing the data values. When writing to a list
            of subarrays, `start` is 2D array of size [num][ndims] and each
            start[i] is a vector specifying the index in the variable where the
            first of the data values will be written.
        :type start: numpy.ndarray

        :param count: [Optional]
            Only relevant when writing a array of values, a subsampled array, a
            mapped array or a list of subarrays.  An array of integers
            specifying  the edge lengths along each dimension of the block of
            data values to be written. The elements of `count` must correspond
            to the variable’s dimensions in order. Hence, if the variable is a
            record variable, the first index would correspond to the starting
            record number for writing the data values. When writing to a list
            of subarrays, `count` is 2D array of size [num][ndims] and each
            count[i] is a vector specifying the edge lengths along each
            dimension of the block of data values to be written.
        :type count: numpy.ndarray

        :param stride: [Optional]
            Only relevant when writing a subsampled array or a mapped array. An
            array of integers specifying the sampling interval along each
            dimension of the netCDF variable. The elements of the stride vector
            correspond, in order, to the netCDF variable’s dimensions.
        :type stride: numpy.ndarray

        :param imap: [Optional]
            Only relevant when writing a subsampled array or a mapped array. An
            array of integers the mapping between the dimensions of a netCDF
            variable and the in-memory structure of the internal data array.
            The elements of the index mapping vector correspond, in order, to
            the netCDF variable’s dimensions. Each element value of imap should
            equal the memory location distance in write buffer between two
            adjacent elements along the corresponding dimension of netCDF
            variable.
        :type imap: numpy.ndarray

        :param bufcount: [Optional]
            Optional for all types of writing patterns. An integer indicates
            the number of MPI derived data type elements in the write buffer to
            be written to the file.
        :type bufcount: int

        :param buftype: [Optional]
            An MPI derived data type that describes the memory layout of the
            write buffer.
        :type buftype: mpi4py.MPI.Datatype

        :Operational mode: This method must be called while the file is in
            collective data mode.

        :Example: A example is available in ``examples/put_var.py``

         ::

           var.put_var_all(buf, start = start, count = count)

           # Equivalently, below uses python index style
           end = [start[i] + count[i] for i in range(2)]
           var[start[0]:end[0], start[1]:end[1]] = buf

        """
        if data is not None and all(arg is None for arg in [start, count, stride, imap]):
            self._put_var(data, collective = True, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start]) and all(arg is None for arg in [count, stride, imap]):
            self._put_var1(data, start, collective = True, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start, count]) and all(arg is None for arg in [stride, imap]):
            self._put_vara(start, count, data, collective = True, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start, count, stride]) and all(arg is None for arg in [imap]):
            self._put_vars(start, count, stride, data, collective = True, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start, count, imap]):
            self._put_varm(data, start, count, stride, imap, collective = True, bufcount = bufcount, buftype = buftype)
        else:
            raise ValueError("Invalid input arguments for put_var_all")


    def put_var(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None):
        """
        put_var(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None)

        Method to write in parallel to the netCDF variable in the independent
        I/O mode. For the argument usage, please refer to method
        :meth:`Variable.put_var_all`. The only difference is this method is a
        independent operation.

        :Operational mode: This method must be called while the file is in
            independent data mode.
        """
        if data is not None and all(arg is None for arg in [start, count, stride, imap]):
            self._put_var(data, collective = False, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start]) and all(arg is None for arg in [count, stride, imap]):
            self._put_var1(data, start, collective = False, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start, count]) and all(arg is None for arg in [stride, imap]):
            self._put_vara(start, count, data, collective = False, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start, count, stride]) and all(arg is None for arg in [imap]):
            self._put_vars(start, count, stride, data, collective = False, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start, count, stride, imap]):
            self._put_varm(data, start, count, stride, imap, collective = False, bufcount = bufcount, buftype = buftype)
        else:
            raise ValueError("Invalid input arguments for put_var")

    def _put(self, ndarray data, start, count, stride):
        """Private method to put data into a netCDF variable"""
        cdef int ierr, ndims
        cdef npy_intp totelem
        cdef size_t *startp
        cdef size_t *countp
        cdef ptrdiff_t *stridep
        cdef char **strdata
        cdef void* elptr
        cdef char* databuff
        cdef ndarray dataarr
        cdef MPI_Offset bufcount
        cdef MPI_Datatype buftype
        # rank of variable.
        ndims = len(self.dimensions)
        # make sure data is contiguous.
        # if not, make a local copy.
        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        # fill up startp,countp,stridep.
        totelem = 1
        negstride = 0
        sl = []
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        stridep = <ptrdiff_t *>malloc(sizeof(ptrdiff_t) * ndims)
        for n from 0 <= n < ndims:
            count[n] = abs(count[n]) # make -1 into +1
            countp[n] = count[n]
            # for neg strides, reverse order (then flip that axis after data read in)
            if stride[n] < 0:
                negstride = 1
                stridep[n] = -stride[n]
                startp[n] = start[n]+stride[n]*(count[n]-1)
                stride[n] = -stride[n]
                sl.append(slice(None, None, -1)) # this slice will reverse the data
            else:
                startp[n] = start[n]
                stridep[n] = stride[n]
                sl.append(slice(None, None, 1))
            totelem = totelem*countp[n]
        # check to see that size of data array is what is expected
        # for slice given.
        dataelem = PyArray_SIZE(data)
        if totelem != dataelem:
            raise IndexError('size of data array does not conform to slice')
        if negstride:
            # reverse data along axes with negative strides.
            data = data[tuple(sl)].copy() # make sure a copy is made.
        if self.dtype != data.dtype:
            data = data.astype(self.dtype) # cast data, if necessary.
        # strides all 1 or scalar variable, use put_vara (faster)
        #bufcount = data.size
        bufcount = 1
        if self._file.file_format != "64BIT_DATA":
            #check if dtype meets CDF-5 variable standards
            if data.dtype.str[1:] not in _supportedtypescdf2:
                raise TypeError, 'illegal data type, must be one of %s, got %s' % \
                (_supportedtypescdf2, data.dtype.str[1:])
        #check if dtype meets CDF-5 variable standards
        elif data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        buftype = MPI_DATATYPE_NULL
        if self._file.indep_mode:
            if sum(stride) == ndims or ndims == 0:
                with nogil:
                    ierr = ncmpi_put_vara(self._file_id, self._varid, \
                                        <const MPI_Offset *>startp, <const MPI_Offset *>countp, \
                                        PyArray_DATA(data), bufcount, buftype)
            else:
                with nogil:
                    ierr = ncmpi_put_vars(self._file_id, self._varid, \
                                        <const MPI_Offset *>startp, <const MPI_Offset *>countp, \
                                        <const MPI_Offset *>stridep, PyArray_DATA(data), bufcount, buftype)
        else:
            if sum(stride) == ndims or ndims == 0:
                with nogil:
                    ierr = ncmpi_put_vara_all(self._file_id, self._varid, \
                                        <const MPI_Offset *>startp, <const MPI_Offset *>countp, \
                                        PyArray_DATA(data), bufcount, buftype)
            else:
                with nogil:
                    ierr = ncmpi_put_vars_all(self._file_id, self._varid, \
                                        <const MPI_Offset *>startp, <const MPI_Offset *>countp, \
                                        <const MPI_Offset *>stridep, PyArray_DATA(data), bufcount, buftype)

        _check_err(ierr)
        free(startp)
        free(countp)
        free(stridep)

    def _get_var1(self, ndarray buff, index, bufcount, MPI.Datatype buftype, collective = True):
        cdef int ierr, ndims
        cdef size_t *indexp
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype

        ndim_index = len(index)
        indexp = <size_t *>malloc(sizeof(size_t) * ndim_index)
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        for i, val in enumerate(index):
            indexp[i] = val
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if collective:
            with nogil:
                ierr = ncmpi_get_var1_all(self._file_id, self._varid, \
                                    <const MPI_Offset *>indexp, PyArray_DATA(buff), buffcount, bufftype)
        else:
            with nogil:
                ierr = ncmpi_get_var1(self._file_id, self._varid, \
                                    <const MPI_Offset *>indexp, PyArray_DATA(buff), buffcount, bufftype)
        _check_err(ierr)
        free(indexp)


    def _get_var(self, ndarray buff, bufcount, MPI.Datatype buftype, collective = True):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef ndarray data
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi

        if collective:
            with nogil:
                ierr = ncmpi_get_var_all(self._file_id, self._varid, \
                                    PyArray_DATA(buff), buffcount, bufftype)
        else:
            with nogil:
                ierr = ncmpi_get_var(self._file_id, self._varid, \
                                    PyArray_DATA(buff), buffcount, bufftype)

        _check_err(ierr)


    def _get_vara(self, ndarray buff, start, count, bufcount, MPI.Datatype buftype, collective = True):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t *startp
        cdef size_t *countp
        ndims = len(self.dimensions)
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        for n from 0 <= n < ndims:
            countp[n] = count[n]
            startp[n] = start[n]

        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if collective:
            with nogil:
                ierr = ncmpi_get_vara_all(self._file_id, self._varid, \
                                        <const MPI_Offset *>startp, <const MPI_Offset *>countp, \
                                        PyArray_DATA(buff), buffcount, bufftype)
        else:
            with nogil:
                ierr = ncmpi_get_vara(self._file_id, self._varid, \
                                        <const MPI_Offset *>startp, <const MPI_Offset *>countp, \
                                        PyArray_DATA(buff), buffcount, bufftype)

        _check_err(ierr)

    def _get_varn(self, ndarray data, num, starts, counts, bufcount, MPI.Datatype buftype, collective = True):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t **startsp
        cdef size_t **countsp
        cdef int num_req

        num_req = num
        ndims = len(self.dimensions)
        max_num_req = len(starts)
        startsp = <size_t**> malloc(max_num_req * sizeof(size_t*));
        for i in range(max_num_req):
            startsp[i] = <size_t*> malloc(ndims * sizeof(size_t));
            for j in range(ndims):
                startsp[i][j] = starts[i][j]

        countsp = <size_t**> malloc(max_num_req * sizeof(size_t*));
        for i in range(max_num_req):
            countsp[i] = <size_t*> malloc(ndims * sizeof(size_t));
            for j in range(ndims):
                countsp[i][j] = counts[i][j]

        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        #bufftype = MPI_DATATYPE_NULL
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi

        if collective:
            with nogil:
                ierr = ncmpi_get_varn_all(self._file_id,
                                          self._varid,
                                          num_req,
                                          <const MPI_Offset **>startsp,
                                          <const MPI_Offset **>countsp,
                                          PyArray_DATA(data),
                                          buffcount,
                                          bufftype)
        else:
            with nogil:
                ierr = ncmpi_get_varn(self._file_id,
                                      self._varid,
                                      num_req,
                                      <const MPI_Offset **>startsp,
                                      <const MPI_Offset **>countsp,
                                      PyArray_DATA(data),
                                      buffcount,
                                      bufftype)

        _check_err(ierr)

    def _get_vars(self, ndarray buff, start, count, stride, bufcount, MPI.Datatype buftype, collective = True):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t *startp
        cdef size_t *countp
        cdef ptrdiff_t *stridep

        ndims = len(self.dimensions)
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        stridep = <ptrdiff_t *>malloc(sizeof(ptrdiff_t) * ndims)
        for n from 0 <= n < ndims:
            countp[n] = count[n]
            startp[n] = start[n]
            stridep[n] = stride[n]
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if collective:
            with nogil:
                ierr = ncmpi_get_vars_all(self._file_id, self._varid, \
                                        <const MPI_Offset *>startp, <const MPI_Offset *>countp, \
                                        <const MPI_Offset *>stridep, PyArray_DATA(buff), buffcount, bufftype)
        else:
            with nogil:
                ierr = ncmpi_get_vars(self._file_id, self._varid, \
                                        <const MPI_Offset *>startp, <const MPI_Offset *>countp, \
                                        <const MPI_Offset *>stridep, PyArray_DATA(buff), buffcount, bufftype)

        _check_err(ierr)

    def _get_varm(self, ndarray buff, start, count, stride, imap, bufcount, MPI.Datatype buftype, collective = True):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t *startp
        cdef size_t *countp
        cdef ptrdiff_t *stridep
        cdef size_t *imapp
        ndims = len(self.dimensions)
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        stridep = <ptrdiff_t *>malloc(sizeof(ptrdiff_t) * ndims)
        imapp = <size_t *>malloc(sizeof(size_t) * ndims)
        for n from 0 <= n < ndims:
            countp[n] = count[n]
            startp[n] = start[n]
            if stride is not None:
                stridep[n] = stride[n]
            else:
                stridep[n] = 1
            imapp[n] = imap[n]
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if collective:
            with nogil:
                ierr = ncmpi_get_varm_all(self._file_id, self._varid, <const MPI_Offset *>startp, \
                                        <const MPI_Offset *>countp, <const MPI_Offset *>stridep, \
                                        <const MPI_Offset *>imapp, PyArray_DATA(buff), buffcount, bufftype)
        else:
            with nogil:
                ierr = ncmpi_get_varm(self._file_id, self._varid, <const MPI_Offset *>startp, \
                                        <const MPI_Offset *>countp, <const MPI_Offset *>stridep, \
                                        <const MPI_Offset *>imapp, PyArray_DATA(buff), buffcount, bufftype)
        _check_err(ierr)

    def get_var_all(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None):
        """
        get_var_all(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None)

        Method to read in parallel from the netCDF variable in the collective
        I/O mode. The behavior of the method varies depends on the pattern of
        provided optional arguments - `start`, `count`, `stride`, and `imap`.
        The method requires a empty array (`data`) as a read buffer from caller
        to store returned array values.

        - `data` - Read an entire variable.
           Read all the values from a netCDF variable of an opened netCDF file.
           This is the simplest interface to use for reading the value of a
           scalar variable or when all the values of a multidimensional
           variable can be read at once.

           .. note:: Be careful when using this simplest form to read a record
              variable when you don’t specify how many records are to be read.
              If you try to read all the values of a record variable into an
              array but there are more records in the file than you assume,
              more data will be read than you expect, which may cause a
              segmentation violation.

        - `data`, `start` - Read a single data value (a single element).
           Put a single array element specified by `start` from a variable of
           an opened netCDF file that is in data mode. For example, start =
           [0,5] would specify the following position in a 4 * 10
           two-dimensional variable ("-" means skip).

           ::

            -  -  -  -  -  a  -  -  -  -
            -  -  -  -  -  -  -  -  -  -      ->   a
            -  -  -  -  -  -  -  -  -  -
            -  -  -  -  -  -  -  -  -  -

        - `data`, `start`, `count` - Read a subarray of values.
           The part of the netCDF variable to read is specified by giving a
           corner index and a vector of edge lengths that refer to an array
           section of the netCDF variable. For example, start = [0,5] and count
           = [2,2] would specify the following array section in a 4 * 10
           two-dimensional variable ("-" means skip).

           ::

            -  -  -  -  -  a  b  -  -  -
            -  -  -  -  -  c  d  -  -  -         a  b
            -  -  -  -  -  -  -  -  -  -     ->  c  d
            -  -  -  -  -  -  -  -  -  -

        - `data`, `start`, `count`, `stride` - Read a subarray of values with strided space.
           The part of the netCDF variable to read is specified by giving a
           corner, a vector of edge lengths and stride vector that refer to a
           subsampled array section of the netCDF variable. For example, start
           = [0,2], count = [2,4] and stride = [1,2] would specify the
           following array section in a 4 * 10 two-dimensional variable ("-"
           means skip).

           ::

            -  -  a  -  b  -  c  -  d  -
            -  -  e  -  f  -  g  -  h  -                a  b  c  d
            -  -  -  -  -  -  -  -  -  -       ->       e  f  g  h
            -  -  -  -  -  -  -  -  -  -

        - `data`, `start`, `count`, `stride`, `imap` - Read a mapped array of values.
           The mapped array section is specified by giving a corner, a vector
           of counts, a stride vector, and an index mapping vector.  The index
           mapping vector (imap) is a vector of integers that specifies the
           mapping between the dimensions of a netCDF variable and the
           in-memory structure of the internal data array. For example, imap =
           [3,8], start = [0,5] and count = [2,2] would specify the following
           section in read butter and array section in a 4 * 10 two-dimensional
           variable ("-" means skip).

           ::

                                       -  -  -  -  -  a  c  -  -  -
            a - - b         a  c       -  -  -  -  -  b  d  -  -  -
            - - - -    <=   b  d  <=   -  -  -  -  -  -  -  -  -  -
            c - - d                    -  -  -  -  -  -  -  -  -  -

            distance from a to b is 3 in buffer => imap[0] = 3
            distance from a to c is 8 in buffer => imap[1] = 8

        :param data:
            the numpy array that stores array values to be read from the file,
            which serves as a read buffer. The datatype should match with the
            variable's datatype. Note this numpy array read buffer can be in
            any shape as long as the number of elements (buffer size) is
            matched.
        :type data: numpy.ndarray

        :param start: [Optional]
            Only relevant when reading a array of values, a subsampled array, a
            mapped array or a list of subarrays.  An array of integers
            specifying the index in the variable where the first of the data
            values will be written. The elements of `start` must correspond to
            the variable’s dimensions in order. Hence, if the variable is a
            record variable, the first index would correspond to the starting
            record number for reading the data values.
        :type start: numpy.ndarray

        :param count: [Optional]
            Only relevant when reading a array of values, a subsampled array, a
            mapped array or a list of subarrays.  An array of integers
            specifying  the edge lengths along each dimension of the block of
            data values to be read. The elements of `count` must correspond
            to the variable’s dimensions in order. Hence, if the variable is a
            record variable, the first index would correspond to the starting
            record number for reading the data values.
        :type count: numpy.ndarray

        :param stride: [Optional]
            Only relevant when reading a subsampled array or a mapped array. An
            array of integers specifying the sampling interval along each
            dimension of the netCDF variable. The elements of the stride vector
            correspond, in order, to the netCDF variable’s dimensions.
        :type stride: numpy.ndarray

        :param imap: [Optional]
            Only relevant when reading a subsampled array or a mapped array. An
            array of integers the mapping between the dimensions of a netCDF
            variable and the in-memory structure of the internal data array.
            The elements of the index mapping vector correspond, in order, to
            the netCDF variable’s dimensions. Each element value of imap should
            equal the memory location distance in read buffer between two
            adjacent elements along the corresponding dimension of netCDF
            variable.
        :type imap: numpy.ndarray

        :param bufcount: [Optional]
            Optional for all types of reading patterns. An integer indicates
            the number of MPI derived data type elements in the read buffer to
            store data read from the file.
        :type bufcount: int

        :param buftype: [Optional]
            An MPI derived data type that describes the memory layout of the
            read buffer.
        :type buftype: mpi4py.MPI.Datatype

        :Operational mode: This method must be called while the file is in
            collective data mode.

        :Example: A example is available in ``examples/get_var.py``

         ::

           # allocate read buffer
           r_buf = np.empty(tuple(count), v.dtype)

           # Read a subarray in collective mode
           v.get_var_all(r_buf, start = start, count = count)

           # Equivalently, below uses python index style
           end = [start[i] + count[i] for i in range(2)]
           r_bufs = v[start[0]:end[0], start[1]:end[1]]

        """
        # Note that get_var requires a empty array as a buffer arg from caller
        # to store returned array values. We understand this is against python
        # API convention. But removing this or making this optional will create
        # two layers of inconsistency that we don't desire:
        # 1. Among all behaviors of get_var get_varm always requires a buffer argument
        # 2. Other i/o methods (iget/put/iput) all require buffer array as mandatory argument

        if all(arg is None for arg in [start, count, stride, imap]):
            self._get_var(data, collective = True, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [start]) and all(arg is None for arg in [count, stride, imap]):
            self._get_var1(data, start, collective = True, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [start, count]) and all(arg is None for arg in [stride, imap]):
            self._get_vara(data, start, count, collective = True, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [start, count, stride]) and all(arg is None for arg in [imap]):
            self._get_vars(data, start, count, stride, collective = True, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [start, count, imap]):
            self._get_varm(data, start, count, stride, imap, collective = True, bufcount = bufcount, buftype = buftype)
        else:
            raise ValueError("Invalid input arguments for get_var_all")

    def get_var(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None):
        """
        get_var(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None)

        Method to read in parallel from the netCDF variable in the independent
        I/O mode.  For the argument usage, please refer to method
        :meth:`Variable.get_var_all`. The only difference is this method is a
        independent operation.

        :Operational mode: This method must be called while the file is in
            independent data mode.
        """
        if all(arg is None for arg in [start, count, stride, imap]):
            self._get_var(data, collective = False, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [start]) and all(arg is None for arg in [count, stride, imap]):
            self._get_var1(data, start, collective = False, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [start, count]) and all(arg is None for arg in [stride, imap]):
            self._get_vara(data, start, count, collective = False, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [start, count, stride]) and all(arg is None for arg in [imap]):
            self._get_vars(data, start, count, stride, collective = False, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [start, count, imap]):
            self._get_varm(data, start, count, stride, imap, collective = False, bufcount = bufcount, buftype = buftype)
        else:
            raise ValueError("Invalid input arguments for get_var")

    def get_varn_all(self, data, num, starts, counts=None, bufcount=None, buftype=None):
        """
        get_varn_all(self, data, num, starts, counts=None, bufcount=None, buftype=None)

        Method to read multiple subarrays of a netCDF variables from the file.
        This a collective  I/O call and can only be called when the file is in
        the collective I/O mode. This method is equivalent to making multiple
        calls to :meth:`Variable.get_var`. Note, combining multiple `get_var`
        calls into one can achieve a better performance.

        - `data`, `num`,`starts`, `counts` -  Write multiple subarrays of values.
           The part of the netCDF variable to read is specified by giving
           multiple subarrays and each subarray is specified by a corner and a
           vector of edge lengths that refer to an array section of the netCDF
           variable.  The example code and diagram below illustrates a 4
           subarray section in a 4 * 10 two-dimensional variable ("-" means
           skip).

           ::

            num = 4

            starts[0][0] = 0; starts[0][1] = 5; counts[0][0] = 1; counts[0][1] = 2
            starts[1][0] = 1; starts[1][1] = 0; counts[1][0] = 1; counts[1][1] = 1
            starts[2][0] = 2; starts[2][1] = 6; counts[2][0] = 1; counts[2][1] = 2
            starts[3][0] = 3; starts[3][1] = 0; counts[3][0] = 1; counts[3][1] = 3

                                 -  -  -  -  -  a  b  -  -  -
            a b c d e f g h  <-  c  -  -  -  -  -  -  -  -  -
                                 -  -  -  -  -  -  d  e  -  -
                                 f  g  h  -  -  -  -  -  -  -

        :param data: the numpy array that stores array values to be read,
            which serves as a read buffer. When reading a single data value,
            it can also be a single numeric (e.g. np.int32) python variable.
            The datatype should match with the variable's datatype. Note this
            numpy array read buffer can be in any shape as long as the number
            of elements (buffer size) is matched. If the in-memory type of data
            values differs from the netCDF variable type defined in the file,
            type conversion will automatically be applied.
        :type data: numpy.ndarray

        :param num: An integer specifying the number of subarrays.
        :type num: int

        :param starts:
            A 2D array of integers containing starting array indices
            of `num` number of subarrays.  The first dimension of `starts`
            should be of size `num`, indicating the number of subarrays of the
            variable to be read. The second dimension is of size equal to
            the number dimensions of the variable.  For example, when `num` = 3
            and the variable defined in the file is a 2D array, `starts` should
            be a 3x2 array.  Each of the subarray starting indices identify
            the indices in the variable where the first of the data values will
            be read. Each `starts[i]` is a vector specifying the index in
            the variable where the first of the data values will be read.
            The elements of `starts[i][*]` must correspond to the variable’s
            dimensions in order.  Hence, if the variable is a record variable,
            the first index, `starts[i][0]` would correspond to the starting
            record number for reading the data values.
        :type starts: numpy.ndarray

        :param counts: [Optional]
            A 2D array of integers specifying the lengths along each
            dimension of `num` number of subarrays to be read. The first
            dimension of `counts` should be of size `num`, indicating the
            number of subarrays of the variable to be read. The second
            dimension is of size equal to the number dimensions of the
            variable.  For example, when `num` = 3 and the variable defined in
            the file is a 2D array, `counts` should be a 3x2 array.  Each of
            the subarray `counts[i]` is a vector specifying the lengths along
            each dimension of the block of data values to be read and must
            correspond to the variable’s dimensions in order.  When this
            argument is not supplied, it is equivalent to providing counts of
            all 1s.
        :type counts: numpy.ndarray

        :param bufcount: [Optional]
            An integer indicates the number of MPI derived data type elements
            in the read buffer to store data read from the file.
        :type bufcount: int

        :param buftype: [Optional]
            An MPI derived data type that describes the memory layout of the
            write buffer.
        :type buftype: mpi4py.MPI.Datatype

        :Example: an example code fragment is given below.

         ::

           num_reqs = 4
           starts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
           counts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
           starts[0][0] = 0; starts[0][1] = 5; counts[0][0] = 1; counts[0][1] = 2
           starts[1][0] = 1; starts[1][1] = 0; counts[1][0] = 1; counts[1][1] = 1
           starts[2][0] = 2; starts[2][1] = 6; counts[2][0] = 1; counts[2][1] = 2
           starts[3][0] = 3; starts[3][1] = 0; counts[3][0] = 1; counts[3][1] = 3

           v.get_varn_all(r_buf, num = num_reqs, starts = starts, counts = counts)

        """
        return self._get_varn(data, num, starts, counts, bufcount = bufcount,
                              buftype = buftype, collective = True)

    def get_varn(self, data, num, starts, counts=None, bufcount=None, buftype=None):
        """
        get_varn(self, data, num, starts, counts=None, bufcount=None, buftype=None)

        This method call is the same as method :meth:`Variable.get_varn_all`,
        except it is an independent call and can only be called while the file
        in the independent I/O mode. Please refer to
        :meth:`Variable.get_varn_all` for its argument usage.
        """
        return self._get_varn(data, num, starts, counts, bufcount = bufcount,
                              buftype = buftype, collective = False)

    def _get(self,start,count,stride):
        """Private method to retrieve data from a netCDF variable"""
        cdef int ierr, ndims, totelem
        cdef size_t *startp
        cdef size_t *countp
        cdef ptrdiff_t *stridep
        cdef ndarray data, dataarr
        cdef void *elptr
        cdef char **strdata
        cdef int file_id = self._file._ncid
        # if one of the counts is negative, then it is an index
        # and not a slice so the resulting array
        # should be 'squeezed' to remove the singleton dimension.
        shapeout = ()
        squeeze_out = False
        for lendim in count:
            if lendim == -1:
                shapeout = shapeout + (1,)
                squeeze_out = True
            else:
                shapeout = shapeout + (lendim,)
        # rank of variable.
        ndims = len(self.dimensions)
        # fill up startp,countp,stridep.
        negstride = 0
        sl = []
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        stridep = <ptrdiff_t *>malloc(sizeof(ptrdiff_t) * ndims)
        for n from 0 <= n < ndims:
            count[n] = abs(count[n]) # make -1 into +1
            countp[n] = count[n]
            # for neg strides, reverse order (then flip that axis after data read in)
            if stride[n] < 0:
                negstride = 1
                stridep[n] = -stride[n]
                startp[n] = start[n]+stride[n]*(count[n]-1)
                stride[n] = -stride[n]
                sl.append(slice(None, None, -1)) # this slice will reverse the data
            else:
                startp[n] = start[n]
                stridep[n] = stride[n]
                sl.append(slice(None,None, 1))

        data = np.empty(shapeout, self.dtype)
        # strides all 1 or scalar variable, use get_vara (faster)
        # if count contains a zero element, no data is being read
        bufcount = 1
        buftype = MPI_DATATYPE_NULL

        if 0 not in count:
            if self._file.indep_mode:
                if sum(stride) == ndims or ndims == 0:
                    with nogil:
                        ierr = ncmpi_get_vara(self._file_id, self._varid,<const MPI_Offset *>startp, \
                        <const MPI_Offset *>countp, PyArray_DATA(data), bufcount, buftype)
                else:
                    with nogil:
                        ierr = ncmpi_get_vars(self._file_id, self._varid, <const MPI_Offset *>startp, \
                        <const MPI_Offset *>countp, <const MPI_Offset *>stridep, PyArray_DATA(data), bufcount, buftype)
            else:
                if sum(stride) == ndims or ndims == 0:
                    with nogil:
                        ierr = ncmpi_get_vara_all(self._file_id, self._varid, <const MPI_Offset *>startp, \
                        <const MPI_Offset *>countp, PyArray_DATA(data), bufcount, buftype)
                else:
                    with nogil:
                        ierr = ncmpi_get_vars_all(self._file_id, self._varid, <const MPI_Offset *>startp, \
                        <const MPI_Offset *>countp, <const MPI_Offset *>stridep, PyArray_DATA(data), bufcount, buftype)
        else:
            ierr = 0
        if ierr == NC_EINVALCOORDS:
            raise IndexError('index exceeds dimension bounds')
        elif ierr != NC_NOERR:
            _check_err(ierr)

        free(startp)
        free(countp)
        free(stridep)
        if negstride:
            # reverse data along axes with negative strides.
            data = data[tuple(sl)].copy() # make a copy so data is contiguous.
        if not self.dimensions:
            return data[0] # a scalar
        elif squeeze_out:
            return np.squeeze(data)
        else:
            return data

    def _iput_var(self, ndarray data, bufcount, MPI.Datatype buftype, buffered = False):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef int request
        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        #data = data.flatten()
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        #bufcount = data.size
        if data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        #bufftype = MPI_DATATYPE_NULL
        if not buffered:
            with nogil:
                ierr = ncmpi_iput_var(self._file_id, self._varid, \
                                        PyArray_DATA(data), buffcount, bufftype, &request)
        else:
            with nogil:
                ierr = ncmpi_bput_var(self._file_id, self._varid, \
                                        PyArray_DATA(data), buffcount, bufftype, &request)
        _check_err(ierr)
        return request

    def _iput_var1(self, value, index, bufcount, MPI.Datatype buftype, buffered=False):
        cdef int ierr, ndims
        cdef size_t *indexp
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef ndarray data
        cdef int request
        # rank of variable.
        data = np.array(value)
        ndim_index = len(index)
        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        indexp = <size_t *>malloc(sizeof(size_t) * ndim_index)
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        for i, val in enumerate(index):
            indexp[i] = val
        if data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if not buffered:
            with nogil:
                ierr = ncmpi_iput_var1(self._file_id, self._varid, <const MPI_Offset *>indexp,\
                                        PyArray_DATA(data), buffcount, bufftype, &request)
        else:
            with nogil:
                ierr = ncmpi_bput_var1(self._file_id, self._varid, <const MPI_Offset *>indexp,\
                                        PyArray_DATA(data), buffcount, bufftype, &request)
        _check_err(ierr)
        return request

    def _iput_vara(self, start, count, ndarray data, bufcount, MPI.Datatype buftype, buffered=False):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t *startp
        cdef size_t *countp
        cdef int request
        ndims = len(self.dimensions)
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        for n from 0 <= n < ndims:
            countp[n] = count[n]
            startp[n] = start[n]
        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        #data = data.flatten()
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        #bufcount = data.size
        if data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if not buffered:
            with nogil:
                ierr = ncmpi_iput_vara(self._file_id, self._varid, <const MPI_Offset *>startp, <const MPI_Offset *>countp,\
                                        PyArray_DATA(data), buffcount, bufftype, &request)
        else:
            with nogil:
                ierr = ncmpi_bput_vara(self._file_id, self._varid, <const MPI_Offset *>startp, <const MPI_Offset *>countp,\
                                        PyArray_DATA(data), buffcount, bufftype, &request)
        _check_err(ierr)
        return request

    def _iput_vars(self, start, count, stride, ndarray data, bufcount, MPI.Datatype buftype, buffered=False):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t *startp
        cdef size_t *countp
        cdef ptrdiff_t *stridep
        cdef int request
        ndims = len(self.dimensions)
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        stridep = <ptrdiff_t *>malloc(sizeof(ptrdiff_t) * ndims)
        for n from 0 <= n < ndims:
            countp[n] = count[n]
            startp[n] = start[n]
            stridep[n] = stride[n]
        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        if data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if not buffered:
            with nogil:
                ierr = ncmpi_iput_vars(self._file_id, self._varid, <const MPI_Offset *>startp, <const MPI_Offset *>countp,\
                                        <const MPI_Offset *>stridep, PyArray_DATA(data), buffcount, bufftype, &request)
        else:
            with nogil:
                ierr = ncmpi_bput_vars(self._file_id, self._varid, <const MPI_Offset *>startp, <const MPI_Offset *>countp,\
                                        <const MPI_Offset *>stridep, PyArray_DATA(data), buffcount, bufftype, &request)
        _check_err(ierr)
        return request

    def _iput_varn(self, ndarray data, num, starts, counts, bufcount, MPI.Datatype buftype, buffered=False):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t **startsp
        cdef size_t **countsp
        cdef int num_req
        cdef int request
        num_req = num
        ndims = len(self.dimensions)
        max_num_req = len(starts)
        startsp = <size_t**> malloc(max_num_req * sizeof(size_t*));
        for i in range(max_num_req):
            startsp[i] = <size_t*> malloc(ndims * sizeof(size_t));
            for j in range(ndims):
                startsp[i][j] = starts[i, j]

        countsp = <size_t**> malloc(max_num_req * sizeof(size_t*));
        for i in range(max_num_req):
            countsp[i] = <size_t*> malloc(ndims * sizeof(size_t));
            for j in range(ndims):
                countsp[i][j] = counts[i, j]

        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        #data = data.flatten()
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        #bufcount = data.size
        if data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if not buffered:
            with nogil:
                ierr = ncmpi_iput_varn(self._file_id,
                                       self._varid,
                                       num_req,
                                       <const MPI_Offset **>startsp,
                                       <const MPI_Offset **>countsp,
                                       PyArray_DATA(data),
                                       buffcount,
                                       bufftype,
                                       &request)
        else:
            with nogil:
                ierr = ncmpi_bput_varn(self._file_id,
                                       self._varid,
                                       num_req,
                                       <const MPI_Offset **>startsp,
                                       <const MPI_Offset **>countsp,
                                       PyArray_DATA(data),
                                       buffcount,
                                       bufftype,
                                       &request)

        _check_err(ierr)
        return request

    def _iput_varm(self, ndarray data, start, count, stride, imap, bufcount, MPI.Datatype buftype, buffered=False):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t *startp
        cdef size_t *countp
        cdef ptrdiff_t *stridep
        cdef size_t *imapp
        cdef int request
        ndims = len(self.dimensions)
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        stridep = <ptrdiff_t *>malloc(sizeof(ptrdiff_t) * ndims)
        imapp = <size_t *>malloc(sizeof(size_t) * ndims)
        for n from 0 <= n < ndims:
            countp[n] = count[n]
            startp[n] = start[n]
            if stride is not None:
                stridep[n] = stride[n]
            else:
                stridep[n] = 1
            imapp[n] = imap[n]
        shapeout = ()
        for lendim in count:
            shapeout = shapeout + (lendim,)
        if not PyArray_ISCONTIGUOUS(data):
            data = data.copy()
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        if data.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type, must be one of %s, got %s' % \
            (_supportedtypes, data.dtype.str[1:])
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        if not buffered:
            with nogil:
                ierr = ncmpi_iput_varm(self._file_id, self._varid, <const MPI_Offset *>startp, <const MPI_Offset *>countp,\
                                        <const MPI_Offset *>stridep, <const MPI_Offset *>imapp, PyArray_DATA(data), buffcount, bufftype, &request)
        else:
            with nogil:
                ierr = ncmpi_bput_varm(self._file_id, self._varid, <const MPI_Offset *>startp, <const MPI_Offset *>countp,\
                                        <const MPI_Offset *>stridep, <const MPI_Offset *>imapp, PyArray_DATA(data), buffcount, bufftype, &request)
        _check_err(ierr)
        return request

    def bput_var(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None):
        """
        bput_var(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None)

        Method to post a nonblocking, buffered write request to write to the
        netCDF variable. The syntax is the same as :meth:`Variable.put_var`.
        For the argument usage, please refer to :meth:`Variable.put_var_all`.
        This method returns a request ID that can be used in
        :meth:`File.wait_all` or :meth:`File.wait`. The posted write request
        may not be committed until :meth:`File.wait_all` or :meth:`File.wait`
        is called.

        .. note:: Note that this method requires a numpy array (`data`) as a
            write buffer from caller prepared for writing returned array values
            when :meth:`File.wait_all` or :meth:`File.wait` is called.
            Unlike :meth:`Variable.iput_var`, the write data is buffered
            (cached) internally by PnetCDF and will be flushed to the file at
            the time of calling :meth:`File.wait_all` or :meth:`File.wait`.
            Once the call to this method returns, the caller is free to change
            the contents of write buffer.  Prior to calling this method, make
            sure :meth:`File.attach_buff` is called to allocate an internal
            buffer for accommodating the write requests.

        :return: The request ID, which can be used in a successive call to
            :meth:`File.wait_all` or :meth:`File.wait` for the completion
            of the nonblocking operation.
        :rtype: int

        :Operational mode: This method can be called while the file is in either
            collective or independent data mode.
        """

        if data is not None and all(arg is None for arg in [start, count, stride, imap]):
            return self._iput_var(data, buffered=True, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start]) and all(arg is None for arg in [count, stride, imap]):
            return self._iput_var1(data, start, buffered=True, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start, count]) and all(arg is None for arg in [stride, imap]):
            return self._iput_vara(start, count, data, buffered=True, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start, count, stride]) and all(arg is None for arg in [imap]):
            return self._iput_vars(start, count, stride, data, buffered=True, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start, count, imap]):
            return self._iput_varm(data, start, count, stride, imap, buffered=True, bufcount = bufcount, buftype = buftype)
        else:
            raise ValueError("Invalid input arguments for bput_var")

    def iput_var(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None):
        """
        iput_var(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None)

        Method to post a nonblocking request to write to the netCDF variable.
        The syntax is the same as :meth:`Variable.put_var`. For the argument
        usage, please refer to :meth:`Variable.put_var_all`. This method
        returns a request ID that can This method returns a request ID that can
        be used in :meth:`File.wait_all` or :meth:`File.wait`. The posted write
        request may not be committed until :meth:`File.wait_all` or
        :meth:`File.wait` is called.

        .. note:: Note that this method requires a numpy array (`data`) as a
            write buffer from caller prepared for writing returned array values
            when :meth:`File.wait_all` or :meth:`File.wait` is called.  Users
            should not alter the contents of the write buffer once the request
            is posted until the :meth:`File.wait_all` or :meth:`File.wait` is
            returned. Any change to the buffer contents in between will result
            in unexpected error.

        :return: The request ID, which can be used in a successive call to
            :meth:`File.wait_all` or :meth:`File.wait` for the completion
            of the nonblocking operation.
        :rtype: int

        :Operational mode: This method can be called while the file is in either
            collective or independent data mode.
        """
        if data is not None and all(arg is None for arg in [start, count, stride, imap]):
            return self._iput_var(data, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start]) and all(arg is None for arg in [count, stride, imap]):
            return self._iput_var1(data, start, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start, count]) and all(arg is None for arg in [stride, imap]):
            return self._iput_vara(start, count, data, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start, count, stride]) and all(arg is None for arg in [imap]):
            return self._iput_vars(start, count, stride, data, bufcount = bufcount, buftype = buftype)
        elif all(arg is not None for arg in [data, start, count, imap]):
            return self._iput_varm(data, start, count, stride, imap, bufcount = bufcount, buftype = buftype)
        else:
            raise ValueError("Invalid input arguments for iput_var")

    def _iget_var(self, ndarray data, bufcount, MPI.Datatype buftype):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef int request
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        with nogil:
            ierr = ncmpi_iget_var(self._file_id, self._varid, PyArray_DATA(data), \
            buffcount, bufftype, &request)
        _check_err(ierr)
        return request


    def _iget_var1(self, ndarray buff, index, bufcount, MPI.Datatype buftype):
        cdef int ierr, ndims
        cdef size_t *indexp
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef int request
        ndim_index = len(index)
        indexp = <size_t *>malloc(sizeof(size_t) * ndim_index)
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        for i, val in enumerate(index):
            indexp[i] = val
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        with nogil:
            ierr = ncmpi_iget_var1(self._file_id, self._varid, \
                                <const MPI_Offset *>indexp, PyArray_DATA(buff), buffcount,\
                                bufftype, &request)
        _check_err(ierr)
        free(indexp)
        return request


    def _iget_vara(self, ndarray data, start, count, bufcount, MPI.Datatype buftype):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t *startp
        cdef size_t *countp
        cdef int request
        ndims = len(self.dimensions)
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        for n from 0 <= n < ndims:
            countp[n] = count[n]
            startp[n] = start[n]
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount

        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        with nogil:
            ierr = ncmpi_iget_vara(self._file_id, self._varid, \
                                    <const MPI_Offset *>startp, <const MPI_Offset *>countp, \
                                    PyArray_DATA(data), buffcount, bufftype, &request)
        _check_err(ierr)
        return request

    def _iget_vars(self, ndarray buff, start, count, stride, bufcount, MPI.Datatype buftype):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t *startp
        cdef size_t *countp
        cdef ptrdiff_t *stridep
        cdef int request
        ndims = len(self.dimensions)
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        stridep = <ptrdiff_t *>malloc(sizeof(ptrdiff_t) * ndims)
        for n from 0 <= n < ndims:
            countp[n] = count[n]
            startp[n] = start[n]
            stridep[n] = stride[n]
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount

        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        with nogil:
            ierr = ncmpi_iget_vars(self._file_id, self._varid, \
                                    <const MPI_Offset *>startp, <const MPI_Offset *>countp, \
                                    <const MPI_Offset *>stridep, PyArray_DATA(buff), buffcount, bufftype, &request)
        _check_err(ierr)
        return request

    def iget_varn(self, ndarray data, num, starts, counts=None, bufcount=None, MPI.Datatype buftype=None):
        """
        iget_varn(self, data, num, starts, counts=None, bufcount=None, buftype=None)

        This method call is the nonblocking counterpart of
        :meth:`Variable.get_varn`. The syntax is the same as
        :meth:`Variable.get_varn`. For the argument usage, please refer to
        method :meth:`Variable.get_varn_all`. This method returns a request ID
        that can be used in :meth:`File.wait_all` or :meth:`File.wait`. The
        posted write request may not be committed until :meth:`File.wait_all`
        or :meth:`File.wait` is called.

        .. note::
            Unlike :meth:`Variable.get_varn`, the posted nonblocking read
            requests may not be committed until the time of calling
            :meth:`File.wait_all` or :meth:`File.wait`.  Users should not
            alter the contents of the read buffer once the request is posted
            until the :meth:`File.wait_all` or :meth:`File.wait` is
            returned. Any change to the buffer contents in between will result
            in unexpected error.

        :return: The request ID, which can be used in a successive call to
            :meth:`File.wait_all` or :meth:`File.wait` for the completion
            of the nonblocking operation.
        :rtype: int
        """

        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t **startsp
        cdef size_t **countsp
        cdef int num_req
        cdef int request
        num_req = num
        ndims = len(self.dimensions)
        max_num_req = len(starts)
        startsp = <size_t**> malloc(max_num_req * sizeof(size_t*));
        for i in range(max_num_req):
            startsp[i] = <size_t*> malloc(ndims * sizeof(size_t));
            for j in range(ndims):
                startsp[i][j] = starts[i][j]

        countsp = <size_t**> malloc(max_num_req * sizeof(size_t*));
        for i in range(max_num_req):
            countsp[i] = <size_t*> malloc(ndims * sizeof(size_t));
            for j in range(ndims):
                countsp[i][j] = counts[i][j]

        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        #bufftype = MPI_DATATYPE_NULL
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        with nogil:
            ierr = ncmpi_iget_varn(self._file_id,
                                   self._varid,
                                   num_req,
                                   <const MPI_Offset **>startsp,
                                   <const MPI_Offset **>countsp,
                                   PyArray_DATA(data),
                                   buffcount,
                                   bufftype,
                                   &request)

        _check_err(ierr)
        return request

    def _iget_varm(self, ndarray buff, start, count, stride, imap, bufcount, MPI.Datatype buftype):
        cdef int ierr, ndims
        cdef MPI_Offset buffcount
        cdef MPI_Datatype bufftype
        cdef size_t *startp
        cdef size_t *countp
        cdef ptrdiff_t *stridep
        cdef size_t *imapp
        cdef int request
        ndims = len(self.dimensions)
        startp = <size_t *>malloc(sizeof(size_t) * ndims)
        countp = <size_t *>malloc(sizeof(size_t) * ndims)
        stridep = <ptrdiff_t *>malloc(sizeof(ptrdiff_t) * ndims)
        imapp = <size_t *>malloc(sizeof(size_t) * ndims)
        for n from 0 <= n < ndims:
            countp[n] = count[n]
            startp[n] = start[n]
            if stride is not None:
                stridep[n] = stride[n]
            else:
                stridep[n] = 1
            imapp[n] = imap[n]
        if bufcount is None:
            buffcount = 1
        else:
            buffcount = bufcount
        if buftype is None:
            bufftype = MPI_DATATYPE_NULL
        else:
            bufftype = buftype.ob_mpi
        with nogil:
            ierr = ncmpi_iget_varm(self._file_id, self._varid, \
                                    <const MPI_Offset *>startp, <const MPI_Offset *>countp, <const MPI_Offset *>stridep, \
                                    <const MPI_Offset *>imapp, PyArray_DATA(buff), buffcount, bufftype, &request)
        _check_err(ierr)
        return request

    def iget_var(self, data=None, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None):
        """
        iget_var(self, data, start=None, count=None, stride=None, imap=None, bufcount=None, buftype=None)

        Method to post a nonblocking request to read from the netCDF variable.
        The syntax is the same as :meth:`Variable.get_var`. For the argument
        usage, please refer to :meth:`Variable.get_var_all`.  This method
        returns a request ID that can be used in :meth:`File.wait_all` or
        :meth:`File.wait`. The posted read request may not be committed until
        :meth:`File.wait_all` or :meth:`File.wait` is called.

        .. note:: Note that this method requires a empty array (`data`) as a
            read buffer from caller prepared for storing returned array values
            when :meth:`File.wait_all` or :meth:`File.wait` is called. User
            is expected to retain this buffer array handler (the numpy
            variable) until the read buffer is committed and the transaction is
            completed.

        :return: The request ID, which can be used in a successive call to
            :meth:`File.wait_all` or :meth:`File.wait` for the completion
            of the nonblocking operation.
        :rtype: int

        :Operational mode: This method can be called in either define,
            collective, or independent data mode.
        """

        if data is not None and all(arg is None for arg in [start, count, stride, imap]):
            return self._iget_var(data, bufcount, buftype)
        elif all(arg is not None for arg in [data, start]) and all(arg is None for arg in [count, stride, imap]):
            return self._iget_var1(data, start, bufcount, buftype)
        elif all(arg is not None for arg in [data, start, count]) and all(arg is None for arg in [stride, imap]):
            return self._iget_vara(data, start, count, bufcount, buftype)
        elif all(arg is not None for arg in [data, start, count, stride]) and all(arg is None for arg in [imap]):
            return self._iget_vars(data, start, count, stride, bufcount, buftype)
        elif all(arg is not None for arg in [data, start, count, imap]):
            return self._iget_varm(data, start, count, stride, imap, bufcount, buftype)
        else:
            raise ValueError("Invalid input arguments for iget_var")

    def inq_offset(self):
        """
        inq_offset(self)

        :return: The starting file offset of this netCDF variable.
        :rtype: int64
        """
        cdef int ierr
        cdef int offset
        with nogil:
            ierr = ncmpi_inq_varoffset(self._file_id, self._varid,
                                       <MPI_Offset *> &offset)
        _check_err(ierr)
        return offset
