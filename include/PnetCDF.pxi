# # size_t, ptrdiff_t are defined in stdlib.h
# cdef extern from "stdlib.h":
#    ctypedef long size_t
#    ctypedef long ptrdiff_t

cdef extern from *:
    ctypedef char* const_char_ptr "const char*"

# Pnetcdf functions.
# TODO: Check nogil
cdef extern from "pnetcdf.h":
    ctypedef int MPI_Comm
    ctypedef int MPI_Info
    ctypedef int MPI_Offset
    ctypedef int nc_type
    ctypedef int MPI_Datatype
    const_char_ptr ncmpi_strerror(int err);
    const_char_ptr ncmpi_strerrno(int err);


    cdef const int NC_BYTE_C "NC_BYTE"
    cdef const int NC_CHAR_C "NC_CHAR"
    cdef const int NC_SHORT_C "NC_SHORT"
    cdef const int NC_INT_C "NC_INT"
    cdef const int NC_LONG_C "NC_LONG"
    cdef const int NC_FLOAT_C "NC_FLOAT"
    cdef const int NC_DOUBLE_C "NC_DOUBLE"
    cdef const int NC_UBYTE_C "NC_UBYTE"
    cdef const int NC_USHORT_C "NC_USHORT"
    cdef const int NC_UINT_C "NC_UINT"
    cdef const int NC_INT64_C "NC_INT64"
    cdef const int NC_UINT64_C "NC_UINT64"

    cdef const int NC_REQ_ALL_C "NC_REQ_ALL"
    cdef const int NC_GET_REQ_ALL_C "NC_GET_REQ_ALL"
    cdef const int NC_PUT_REQ_ALL_C "NC_PUT_REQ_ALL"

    cdef enum:
    # TODO: Fix redeclaration warnings
        NC_NAT # NAT = 'Not A Type' (c.f. NaN)
        #NC_BYTE # signed 1 byte integer
        #NC_CHAR # ISO/ASCII character
        #NC_SHORT # signed 2 byte integer
        #NC_INT # signed 4 byte integer
        #NC_LONG # deprecated, but required for backward compatibility.
        #NC_FLOAT # single precision floating point number
        #NC_DOUBLE # double precision floating point number
        #NC_UBYTE # unsigned 1 byte int
        #NC_USHORT # unsigned 2-byte int
        #NC_UINT # unsigned 4-byte int
        #NC_INT64 # signed 8-byte int
        #NC_UINT64 # unsigned 8-byte int

        NC_NOCLOBBER # Don't destroy existing file on create
        NC_64BIT_OFFSET
        NC_64BIT_DATA
        NC_NOWRITE
        NC_WRITE
        NC_NOERR

        #Default fill values, used unless _FillValue attribute is set.
        # These values are stuffed into newly allocated space as appropriate.
        # The hope is that one might use these to notice that a particular datum
        # has not been set.
        NC_FILL_BYTE
        NC_FILL_CHAR
        NC_FILL_SHORT
        NC_FILL_INT
        NC_FILL_FLOAT
        NC_FILL_DOUBLE
        NC_FILL_UBYTE
        NC_FILL_USHORT
        NC_FILL_UINT
        NC_FILL_INT64
        NC_FILL_UINT64
        # These maximums are enforced by the interface, to facilitate writing
        # applications and utilities.  However, nothing is statically allocated to
        # these sizes internally.
        NC_MAX_DIMS
        NC_MAX_ATTRS
        NC_MAX_VARS
        NC_MAX_NAME
        NC_MAX_VAR_DIMS
        # 'size' argument to ncdimdef for an unlimited dimension
        NC_UNLIMITED
        # attribute id to put/get a global attribute
        NC_GLOBAL
        # All return integer error status.
        # These are the possible values, in addition to certain
        #ncmpi_put_att_<type>
        NC_EBADID
        NC_EPERM
        NC_ENOTVAR
        NC_EGLOBAL
        NC_EINVAL
        NC_EBADNAME
        NC_EBADTYPE
        NC_ESTRICTCDF2
        NC_ECHAR
        NC_ENOTINDEFINE
        NC_EMAXATTS
        NC_EMULTIDEFINE_ATTR_NAME
        NC_EMULTIDEFINE_ATTR_LEN
        NC_EMULTIDEFINE_ATTR_TYPE
        NC_EMULTIDEFINE_ATTR_VAL
        NC_EMULTIDEFINE_FNC_ARGS
        NC_EINVALCOORDS
        NC_EEDGE
        NC_ERANGE
        NC_EINDEFINE
        NC_ENOMEM
        NC_ENOTINDEP
        NC_EIOMISMATCH
        NC_ENOTSUPPORT
        NC_COUNT_IGNORE
        NC_REQ_NULL


        MPI_DATATYPE_NULL
        MPI_CHAR
        MPI_BYTE
        MPI_UNSIGNED_CHAR
        MPI_SHORT
        MPI_UNSIGNED_SHORT
        MPI_INT
        MPI_UNSIGNED
        MPI_LONG_LONG
        MPI_UNSIGNED_LONG_LONG
        MPI_FLOAT
        MPI_DOUBLE





    # File APIs
    int ncmpi_create(MPI_Comm comm, const char *path, int cmode, MPI_Info info, int *ncidp) nogil
    int ncmpi_open(MPI_Comm comm, const char *path, int cmode, MPI_Info info, int *ncidp) nogil
    int ncmpi_close(int ncid) nogil
    int ncmpi_enddef(int ncid) nogil
    int ncmpi_redef(int ncid) nogil
    int ncmpi_sync(int ncid) nogil
    int ncmpi_begin_indep_data(int ncid) nogil;
    int ncmpi_end_indep_data(int ncid) nogil;
    int ncmpi_inq_path(int ncid, int *pathlen, char *path) nogil
    # Dimension APIs
    int ncmpi_def_dim(int ncid, const char *name, MPI_Offset len, int *idp) nogil
    # Inquiry APIs
    int ncmpi_inq(int ncid, int *ndimsp, int *nvarsp, int *ngattsp, int *unlimdimidp) nogil
    int ncmpi_inq_ndims(int ncid, int *ndimsp) nogil
    int ncmpi_inq_dimlen(int ncid, int dimid, MPI_Offset *lenp) nogil
    int ncmpi_inq_dimname(int ncid, int dimid, char *name) nogil
    int ncmpi_inq_varnatts(int ncid, int varid, int *nattsp) nogil
    int ncmpi_inq_nvars(int ncid, int *nvarsp) nogil
    int ncmpi_inq_vardimid(int ncid, int varid, int *dimidsp) nogil
    int ncmpi_inq_var_fill(int ncid, int varid, int *no_fill, void *fill_value) nogil
    # Attibute APIs
    int ncmpi_put_att_text(int ncid, int varid, const char *name, MPI_Offset len, const char *op) nogil
    int ncmpi_put_att(int ncid, int varid, const char *name, nc_type xtype, MPI_Offset len, const void *op) nogil
    int ncmpi_inq_att(int ncid, int varid, const char *name, nc_type *xtypep, MPI_Offset *lenp) nogil
    int ncmpi_inq_natts(int ncid, int *ngattsp) nogil
    int ncmpi_inq_attname(int ncid, int varid, int attnum, char *name) nogil

    int ncmpi_get_att(int ncid, int varid, const char *name, void *ip) nogil
    int ncmpi_get_att_text(int ncid, int varid, const char *name, char *ip) nogil

    int ncmpi_rename_att(int ncid, int varid, const char *name, const char *newname) nogil
    int ncmpi_del_att(int ncid, int varid, const char *name) nogil
    #Variable APIs
    int ncmpi_def_var(int ncid, const char *name, nc_type xtype, int ndims, const int *dimidsp, int *varidp) nogil
    int ncmpi_def_var_fill(int ncid, int varid, int no_fill, const void *fill_value) nogil
    int ncmpi_inq_varndims(int ncid, int varid, int *ndimsp) nogil
    int ncmpi_inq_varname(int ncid, int varid, char *name) nogil
    int ncmpi_inq_vartype(int ncid, int varid, nc_type *xtypep) nogil
    int ncmpi_put_vara(int ncid, int varid, const MPI_Offset start[], const MPI_Offset count[],\
     const void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_put_vara_all(int ncid, int varid, const MPI_Offset start[], const MPI_Offset count[],\
     const void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_put_vars(int ncid, int varid, const MPI_Offset start[], const MPI_Offset count[],\
     const MPI_Offset stride[], const void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_put_vars_all(int ncid, int varid, const MPI_Offset start[], const MPI_Offset count[],\
     const MPI_Offset stride[], const void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_put_var1_all(int ncid, int varid, const MPI_Offset index[], const void *buf, MPI_Offset bufcount,\
     MPI_Datatype buftype) nogil
    int ncmpi_put_var1(int ncid, int varid, const MPI_Offset index[], const void *buf, MPI_Offset bufcount,\
     MPI_Datatype buftype) nogil
    int ncmpi_put_var(int ncid, int varid, const void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_put_var_all(int ncid, int varid, const void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_put_varn(int ncid, int varid, int num, MPI_Offset* const starts[], MPI_Offset* const counts[], const void *buf,\
     MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_put_varn_all(int ncid, int varid, int num, MPI_Offset* const starts[], MPI_Offset* const counts[], const void *buf,\
     MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_put_varm(int ncid, int varid, const MPI_Offset start[], const MPI_Offset count[], const MPI_Offset stride[], \
    const MPI_Offset imap[], const void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_put_varm_all(int ncid, int varid, const MPI_Offset start[], const MPI_Offset count[], const MPI_Offset stride[], \
    const MPI_Offset imap[], const void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil

    int ncmpi_get_vara(int ncid, int varid, const MPI_Offset start[],\
     const MPI_Offset count[], void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_get_vara_all(int ncid, int varid, const MPI_Offset start[],\
    const MPI_Offset count[], void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_get_vars(int ncid, int varid, const MPI_Offset start[],\
    const MPI_Offset count[], const MPI_Offset stride[], void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_get_vars_all(int ncid, int varid, const MPI_Offset start[], const MPI_Offset count[],\
    const MPI_Offset stride[], void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_get_var1(int ncid, int varid, const MPI_Offset index[], void *buf, \
    MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_get_var1_all(int ncid, int varid, const MPI_Offset index[], void *buf, \
    MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_get_var_all(int ncid, int varid, void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_get_var(int ncid, int varid, void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_get_varn_all(int ncid, int varid, int num, MPI_Offset* const starts[], MPI_Offset* const counts[],\
     void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_get_varn(int ncid, int varid, int num, MPI_Offset* const starts[], MPI_Offset* const counts[],\
     void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_get_varm(int ncid, int varid, const MPI_Offset start[], const MPI_Offset count[], const MPI_Offset stride[],\
     const MPI_Offset imap[], void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_get_varm_all(int ncid, int varid, const MPI_Offset start[], const MPI_Offset count[], const MPI_Offset stride[],\
     const MPI_Offset imap[], void *buf, MPI_Offset bufcount, MPI_Datatype buftype) nogil
    int ncmpi_iput_var(int ncid, int varid, const void *buf, MPI_Offset bufcount, MPI_Datatype buftype, int *request) nogil
    int ncmpi_iput_vara(int ncid, int varid, const MPI_Offset start[], const MPI_Offset count[], const void *buf, \
    MPI_Offset bufcount, MPI_Datatype buftype, int *request) nogil
    int ncmpi_iget_var(int ncid, int varid, void *buf, MPI_Offset bufcount, MPI_Datatype buftype, int *request) nogil
    int ncmpi_iget_vara(int ncid, int varid, const MPI_Offset start[], const MPI_Offset count[], void *buf, MPI_Offset bufcount,\
     MPI_Datatype buftype, int *request) nogil
    int ncmpi_wait(int ncid, int count, int array_of_requests[], int array_of_statuses[]) nogil
    int ncmpi_wait_all(int ncid, int count, int array_of_requests[], int array_of_statuses[]) nogil
# taken from numpy.pxi in numpy 1.0rc2.
cdef extern from "numpy/arrayobject.h":
    ctypedef int npy_intp 
    ctypedef extern class numpy.ndarray [object PyArrayObject]:
        pass
    npy_intp PyArray_SIZE(ndarray arr) nogil
    npy_intp PyArray_ISCONTIGUOUS(ndarray arr) nogil
    npy_intp PyArray_ISALIGNED(ndarray arr) nogil
    void* PyArray_DATA(ndarray) nogil
    char* PyArray_BYTES(ndarray) nogil
    npy_intp* PyArray_STRIDES(ndarray) nogil
    void import_array()