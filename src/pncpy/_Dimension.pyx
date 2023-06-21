from ._File cimport File
from ._utils cimport _strencode, _check_err
cimport mpi4py.MPI as MPI

ctypedef MPI.Offset Offset


from libc.string cimport memcpy, memset
from libc.stdlib cimport malloc, free
from mpi4py.libmpi cimport MPI_Offset

include "PnetCDF.pxi"

cdef class Dimension:
    def __init__(self, File file, name, size=-1, **kwargs):
        self._dimid = 0
        self._file = file
        """
        **`__init__(self, File file, name, Offset size = None, **kwargs)`**
        `Dimension` constructor.
        **`file`**: `File` instance to associate with dimension.
        **`name`**: Name of the dimension.
        **`size`**: Size of the dimension. -1 means unlimited. (Default `-1`).
        ***Note***: `Dimension` instances should be created using the
        `Dataset.def_dim` method of a `File` instance, not using `Dimension.__init__` directly.
        """
        cdef int ierr
        cdef char *dimname
        cdef MPI_Offset lendim
        self._file_id = file._ncid
        self._file_format = file.file_format
        self._name = name

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
            return 'Dimension object no longer valid'
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

        Return the file that this ``Dimension`` is a member of.

        :rtype: :class:`pncpy.File`
        """
        return self._file

    def isunlimited(self):
        """
        isunlimited(self)

        Returns `True` if the ``Dimension`` instance is unlimited, ``False`` otherwise.
        
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


