.. currentmodule:: pnetcdf
=================================
Comparing with netCDF4-python API
=================================

PnetCDF-python programming in a way is very similar to netCDF4-python.
However, there are some differences as listed below.

Supported File Formats
--------------------------

 NetCDF4-python supports NETCDF4 format (HDF5) in addition to classic netCDF
 formats (NETCDF3_CLASSIC, NETCDF3_64BIT_OFFSET, NETCDF3_64BIT_DATA). However,
 PnetCDF-python library only supports netCDF classic file formats, which means
 all netCDF4-dependent features are **not** supported, including user-defined
 types, compound data types, compression, hierarchical structure, etc.

Difference in Programming Model
--------------------------------

 Data/Define Mode
  NetCDF4-python library automatically switches between data and define mode
  for the user by calling ``redef`` and ``enddef`` internally within the
  define-mode operation functions. For performance reason, this is **not**
  adopted in Pnetcdf-python. A manual call to :meth:`File.redef` is compulsory
  to re-enter the define mode, following the C library convention. Similarly,
  :meth:`File.enddef` is required before switching to data mode operations.
  This design is based on considerations of the following aspects:

  - Minimize overheads during consecutive define operations: Automatically
    wrapping all define functions with :meth:`File.redef` and
    :meth:`File.enddef` could introduce significant overhead between
    consecutive define operations. The netCDF4-python approach results in
    unnecessary data/define mode switches, impacting performance.

  - Avoid potential hanging when performing independent I/O: if
    :meth:`File.enddef` is automatically embedded in all data mode operation
    functions, the program will hang when partial processes are performing
    independent I/O (while others don't) because :meth:`File.enddef` is a
    collective call which requires all processes to participate.

 Independent/Collective I/O Mode
  There are two types of parallel I/O operations, independent I/O and
  collective I/O supported both in PnetCDF-python and netCDF4-python.
  NetCDF4-python toggles back and forth between the two types at
  variable-level. However, PnetCDF-python manages this at file-level through
  :meth:`File.begin_indep` and :meth:`File.end_indep`. The default I/O mode is
  collective I/O in PnetCDF-python.


Alternative Reads and Writes Methods
------------------------------------------

 For reading from and writing to netCDF4 variables, PnetCDF-python provides
 alternative methods in addition to numpy-like indexer syntax. The
 :meth:`Variable.get_var` and :meth:`Variable.put_var` methods are faithful
 python-implementations of the put/get_var families from the original PnetCDF-C
 library. By overloading the input arguments, these methods can fulfill
 specific I/O needs to the target variable depending on the requirements of the
 applications: the entire variable, a single data value, a subarray of values,
 a mapped array or a list of subarrays. These methods require an array argument
 as read/write buffer, which is a prerequisite non-blocking I/O as introduced
 below.

 An example program can be found in ``examples/get_vara.py``.

Nonblocking I/O
------------------------------------------
 In additional to blocking read/write APIs, PnetCDF also offers the nonblocking
 APIs that lets users to post multiple requests and subsequently flush them
 altogether. This feature allows PnetCDF to improve performance by aggregating
 small I/O requests and maximizing I/O bandwidth utilization. This feature
 implemented in PnetCDF-C library is faithfully preserved in PnetCDF-python
 nonblocking APIs.

 An example program can be found in ``examples/nonblocking/nonblocking_write.py``.

