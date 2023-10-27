.. currentmodule:: pncpy
=================================
Comparing with netCDF4-python API
=================================
.. warning::

   Under construction. 

PnetCDF-python inherits many features from netCDF4-python, making the transition from the former to the latter a seamless process 
for most netCDF4-python applications. However, there are some exceptions to this as listed below. On the other hand, PnetCDF supported 
some new APIs not available in netCDF4-python.  

Supported File Formats
--------------------------

 NetCDF4-python supports version NETCDF4 formats(HDF5) in addition to classic netCDF formats(NETCDF3_CLASSIC, NETCDF3_64BIT_OFFSET, NETCDF3_64BIT_DATA). However,
 PnetCDF-python library only supports netCDF classic file formats, which means all netCDF4-dependent features are **not** supported, including user-defined types, 
 compression, hirarchical structure, etc.

Difference in Programming Model
--------------------------------

 Data/Define Mode
  NetCDF4-python library automatically switches between data and define mode for the user by calling ``redef`` and ``enddef`` internally within the define-mode 
  operation functions, which is **not** implemented in Pnetcdf-python. A manual call to :meth:`File.redef` is compulsory to activate define mode before swtiching 
  to define mode opearations, following the C library convention. Similarly, :meth:`File.enddef` is required before switching to data mode operations. This design is based on considerations of 
  the following aspects:

  - Minimize overheads during consecutive define operations: Automatically wrapping all define functions with :meth:`File.redef` and :meth:`File.enddef` could introduce 
    significant overhead between consecutive define operations. This approach results in unnecessary data/define mode switches, impacting performance.
  - Avoid potential hanging when performing independent I/O: if :meth:`File.enddef` is automatically embeded in all data mode operation functions, the program will hang when 
    partial processes are performing independent I/O(while others don't) because :meth:`File.enddef` is a collective call which requires all processes to participate.

 Independent/Collective I/O Mode
  There are two types of parallel IO, independent (the default) and collective supported both in PnetCDF-python and netCDF4-python. NetCDF4-python toggles back and forth
  between the two types at variable-level. However, PnetCDF-python manages this at file-level through :meth:`File.begin_indep` and :meth:`File.end_indep`.
 

Alternative Reads and Writes Methods
------------------------------------------

 For reading from and writing to netCDF4 variables, PnetCDF-python provides alternative methods in addition to numpy-like indexer syntax. The :meth:`pncpy.Variable.get_var` and
 :meth:`pncpy.Variable.put_var` methods are faithfull python-implementations of the put/get_var families from the original PnetCDF-C library. By overloading the input arguments, 
 these methods can fulfill specific I/O needs to the target variable depending on the requirements of the applications: the entire variable, a single data value, an 
 (subsampled) array of values, a mapped array or a list of subarrays. These methods require an array argument as read/write buffer, which is a prerequisite non-blocking 
 I/O as introduced below.

Non-blocking I/O
------------------------------------------
 In additional to blocking read/writes, PnetCDF also offers the nonblocking API that enables users to initiate multiple requests without actually doing I/O and subsequently 
 flush them altogether. This approach is designed to enhance performance by merging small I/O requests and maximizing I/O efficiency. This features is faithfully 
 preserved in PnetCDF-python API. 
