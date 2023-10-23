===========================
Datatype 
===========================
.. warning::

   Under construction. 

NetCDF Variable Types
 The following table gives the netCDF external data types defined in CDF-1 and CDF-2 and the corresponding type constants for 
 defining variables in the python interface. All these data types have direct numpy quivalent.



      +-------+----------------+-------+----------------------------------------+---------------------+
      | Type  | NC Constants   | Bits  | Intent of use                          | Numpy Equivalent    |
      +=======+================+=======+========================================+=====================+
      | char  | NC_CHAR        | 8     | text data                              | np.int8 or 'i1'     |
      +-------+----------------+-------+----------------------------------------+---------------------+
      | byte  | NC_BYTE        | 8     | 1-byte integer*                        | np.int8 or 'i1'     |
      +-------+----------------+-------+----------------------------------------+---------------------+
      | short | NC_SHORT       | 16    | 2-byte signed integer                  | np.int16 or 'i2'    |
      +-------+----------------+-------+----------------------------------------+---------------------+
      | int   | NC_INT         | 32    | 4-byte signed integer                  | np.int32 or 'i4'    |
      +-------+----------------+-------+----------------------------------------+---------------------+
      | float | NC_FLOAT       | 32    | 4-byte floating point number           | np.float32 or 'f4'  |
      +-------+----------------+-------+----------------------------------------+---------------------+
      | double| NC_DOUBLE      | 64    | 8-byte real number in double precision | np.float64 or 'f8'  |
      +-------+----------------+-------+----------------------------------------+---------------------+


 New data types supported in CDF-5 format:

      +---------------------+----------------+-------+----------------------------------------+---------------------+
      | Type                | C #define      | Bits  | Intent of use                          | Numpy Equivalent    |
      +=====================+================+=======+========================================+=====================+
      | unsigned byte       | NC_UBYTE       | 8     | unsigned 1-byte integer                | np.uint8 or 'u1'    |
      +---------------------+----------------+-------+----------------------------------------+---------------------+
      | unsigned short      | NC_USHORT      | 16    | unsigned 2-byte integer                | np.uint16 or 'u2'   |
      +---------------------+----------------+-------+----------------------------------------+---------------------+
      | unsigned int        | NC_UINT        | 32    | unsigned 4-byte integer                | np.uint32 or 'u4'   |
      +---------------------+----------------+-------+----------------------------------------+---------------------+
      | long long           | NC_INT64       | 64    | signed 8-byte integer                  | np.int64 or 'i8'    |
      +---------------------+----------------+-------+----------------------------------------+---------------------+
      | unsigned long long  | NC_UINT64      | 64    | unsigned 8-byte integer                | np.uint64 or 'u8'   |
      +---------------------+----------------+-------+----------------------------------------+---------------------+
