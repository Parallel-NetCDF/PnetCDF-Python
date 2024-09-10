###############################################################################
#
#  Copyright (C) 2024, Northwestern University and Argonne National Laboratory
#  See COPYRIGHT notice in top-level directory.
#
###############################################################################

from ._File cimport File
from ._utils cimport _strencode, _check_err
cimport mpi4py.MPI as MPI

from libc.string cimport memcpy, memset
from libc.stdlib cimport malloc, free

include "PnetCDF.pxi"

cdef class Dimension:
    def __init__(self, File file, name, size=-1, **kwargs):
        """
        __init__(self, File file, name, size=-1, **kwargs)

        The constructor for :class:`pnetcdf.Dimension`.

        :param file: An :class:`pnetcdf.File` instance to associate with dimension.
        :type file: :class:`pnetcdf.File`

        :param name: Name of the new dimension.
        :type name: str

        :param size: Length of the dimension. ``-1`` means to create the
            expandable dimension. (Default ``-1``).
        :type size: int

        :return: The created dimension instance.
        :rtype: :class:`pnetcdf.Dimension`

        .. note:: ``Dimension`` instances should be created using the
            :meth:`File.def_dim` method of a ``File`` instance, not using
            :meth:`Dimension.__init__` directly.

        :Example: A example is available in ``examples/put_var.py``

         ::

           # Define dimensions
           dim_t = f.def_dim('time', size = -1)
           dim_y = f.def_dim("Y",    size = 100)
           dim_x = f.def_dim("X",    size = 200)

        """
        cdef int ierr
        cdef char *dimname
        cdef MPI_Offset lendim
        self._file_id = file._ncid
        self._file_format = file.file_format
        self._name = name
        self._dimid = 0
        self._file = file

        if 'id' in kwargs:
            self._dimid = kwargs['id']
        else:
            bytestr = _strencode(name)
            dimname = bytestr
            if size == -1:
                lendim = NC_UNLIMITED
            else:
                lendim = size
            with nogil:
                ierr = ncmpi_def_dim(self._file_id, dimname, lendim, &self._dimid)
            _check_err(ierr)

    def _getname(self):
        # private method to get name associated with instance.
        cdef int err, _file_id
        cdef char namstring[NC_MAX_NAME+1]

        with nogil:
            ierr = ncmpi_inq_dimname(self._file_id, self._dimid, namstring)
        _check_err(ierr)
        return namstring.decode('utf-8')

    property name:
        """String name of Dimension instance"""
        def __get__(self):
            return self._getname()
        def __set__(self,value):
            raise AttributeError("name cannot be altered")

    property size:
        """Current size of Dimension (calls ``len`` on Dimension instance)"""
        def __get__(self):
            return len(self)
        def __set__(self,value):
            raise AttributeError("size cannot be altered")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if not dir(self._file):
            return 'Dimension is not valid'
        if self.isunlimited():
            return "%r (unlimited): name = '%s', size = %s" %\
                (type(self), self._name, len(self))
        else:
            return "%r: name = '%s', size = %s" %\
                (type(self), self._name, len(self))

    def __len__(self):
        # len(`Dimension` instance) returns current size of dimension
        cdef int ierr
        cdef MPI_Offset lengthp
        with nogil:
            ierr = ncmpi_inq_dimlen(self._file_id, self._dimid, &lengthp)
        _check_err(ierr)
        return lengthp

    def getfile(self):
        """
        getfile(self)

        :return: the ``pnetcdf.File`` instance that this ``Dimension`` belongs to.

        :rtype: :class:`pnetcdf.File`
        """
        return self._file

    def isunlimited(self):
        """
        isunlimited(self)

        :return: ``True`` if this ``Dimension`` instance is unlimited, ``False``
            otherwise.

        :rtype: bool
        """
        cdef int ierr, n, numunlimdims, ndims, nvars, ngatts, xdimid
        cdef int *unlimdimids
        with nogil:
            ierr = ncmpi_inq(self._file_id, &ndims, &nvars, &ngatts, &xdimid)
        if self._dimid == xdimid:
            return True
        else:
            return False


