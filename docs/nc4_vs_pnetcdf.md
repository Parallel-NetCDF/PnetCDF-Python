# Difference between NetCDF4-python and PnetCDF-python

* [Supported File Formats](#supported-file-formats)
* [Differences in Python Programming](#differences-in-python-programming)
* [Blocking vs. Nonblocking APIs](#blocking-vs-nonblocking-apis)

---

## Supported File Formats
* NetCDF4 supports both classic and HDF5-based file formats.
  + Classic file format (CDF-1) -- The ESDS Community Standard defined the file format
    to be used in the NetCDF user community in 1989. The file header bears a
    signature of character string 'CDF-1' and now is commonly referred to as
    'CDF-1' file format.
    * 'CDF-2' format -- The CDF-1 format was later extended to support large
      file size (i.e.  larger than 2GB) in 2004. See its specification in
      [ESDS-RFC-011v2.0](https://cdn.earthdata.nasa.gov/conduit/upload/496/ESDS-RFC-011v2.00.pdf).
      Because its file header bears a signature of 'CDF-2' and the format is
      also commonly referred to as 'CDF-2' format.
    * 'CDF-5' format -- The CDF-2 format was extended by PnetCDF developer team
      in 2009 to support large variables and additional large data types, such
      as 64-bit integer.
  + HDF5-based file format -- Starting from its version 4.0.0, NetCDF includes
    the format that is based on HDF5, which is referred to as NetCDF-4 format.
    This offer new features such as groups, compound types, variable length
    arrays, new unsigned integer types, etc.
* PnetCDF supports only the classic file formats.
  + The classic files created by applications using NetCDF4 library can be read
    by the PnetCDF library and vice versa.
  + PnetCDF provides parallel I/O for accessing files in the classic format.
    NetCDF4's parallel I/O for classic files makes use of PnetCDF library
    underneath. Such feature can be enabled when building NetCDF4 library.

---

## Differences in Python Programming
* Table below shows two python example codes and their differences.
  + Both example codes create a new file, define dimensions, define a variable
    named `WIND` of type `NC_DOUBLE` and then write to it in the collective I/O
    mode.
  + The differences are marked in colors, ${\textsf{\color{green}green}}$ for
    NetCDF4 and ${\textsf{\color{blue}blue}}$ for PnetCDF.

| NetCDF4 | PnetCDF |
|:-------|:--------|
| # import python module<br>import ${\textsf{\color{green}netCDF4}}$ | # import python module<br>import ${\textsf{\color{blue}pnetcdf}}$ |
| ... ||
| # create a new file<br>${\textsf{\color{green}f = netCDF4.Dataset}}$(filename="testfile.nc", mode="w", comm=comm, ${\textsf{\color{green}parallel=True}}$) | # create a new file<br>${\textsf{\color{blue}f = pnetcdf.File}}$(filename="testfile.nc", mode='w', comm=comm) |
| # add a global attributes<br>f.history = "Wed Mar 27 14:35:25 CDT 2024" | ditto NetCDF4 |
| # define dimensions<br>lat_dim = f.createDimension("lat", 360)<br>lon_dim = f.createDimension("lon", 720)<br>time_dim = f.createDimension("time", None) | ditto NetCDF4 |
| # define a 3D variable of NC_DOUBLE type<br>var = f.createVariable(varname="WIND", datatype="f8", dimensions = ("time", "lat", "lon")) | ditto NetCDF4 |
| # add attributes to the variable<br>var.long_name="atmospheric wind velocity magnitude"<br>var.units = "m/s" | ditto NetCDF4 |
| ... ||
| ${\textsf{\color{green}\\# NetCDF4-python requires no explicit define/data mode switching}}$ | ${\textsf{\color{blue}\\# exit define mode and enter data mode}}$<br>${\textsf{\color{blue}f.enddef()}}$ | |
| # allocate and initialize the write buffer<br>buff = np.zeros(shape = (5, 10), dtype = "f8") | ditto NetCDF4 |
| ... ||
| ${\textsf{\color{green}\\# switch to collective I/O mode, default is independent in NetCDF4}}$<br>${\textsf{\color{green}var.set\\_collective(True)}}$ | ${\textsf{\color{blue}\\# collective I/O mode is default in PnetCDF}}$ |
| # write to variable WIND in the file<br>var[0, 5:10, 0:10] = buff | ditto NetCDF4 |
| ... ||
| # close file<br>f.close() | ditto NetCDF4 |

---

## Blocking vs Nonblocking APIs
* Blocking APIs -- All NetCDF4 APIs are blocking APIs. A blocking API means the
  call to the API will not return until the operation is completed. For
  example, `nc_put_vara_float()` will return only when the write data has been
  stored at the system space, e.g. file systems. Similarly,
  `nc_get_vara_float()` will only return when the user read buffer containing
  the data retrieved from the file. Therefore, when a series of `put/get`
  blocking APIs are called, these calls will be committed by the NetCDF4
  library one at a time, following the same order of the calls.
* Nonblocking APIs -- In addition to blocking APIs, PnetCDF provides the
  nonblocking version of the APIs. A nonblocking API means the call to the API
  will return as soon as the `put/get` request has been registered in the
  PnetCDF library. The commitment of the request may happen later, when a call
  to `ncmpi_wait_all/ncmpi_wait` is made. The nonblocking APIs are listed below.
  + Variable.iput_var() - posts a nonblocking request to write to a variable.
  + Variable.iget_var() - posts a nonblocking request to from from a variable.
  + Variable.bput_var() - posts a nonblocking, buffered request to write to a variable.
  + Variable.iput_varn() - posts a nonblocking request to write multiple subarrays to a variable.
  + Variable.iget_varn() - posts a nonblocking request to read multiple subarrays from a variable.
  + Variable.bput_varn() - posts a nonblocking, buffered request to write multiple subarrays to a variable.
  + File.wait_all() - waits for nonblocking requests to complete, using collective MPI-IO.
  + File.wait() - waits for nonblocking requests to complete, using independent MPI-IO.
  + File.attach_buff() - Let PnetCDF to allocate an internal buffer to cache bput write requests.
  + File.detach_buff() - Free the attached buffer.
* The advantage of using nonblocking APIs is when there are many small
  `put/get` requests and each of them has a small amount.  PnetCDF tries to
  aggregate and coalesce multiple registered nonblocking requests into a large
  one, because I/O usually performs better when the request amounts are large
  and contiguous. [nonblocking_write.py](../examples/nonblocking_write.py) is
  an example that makes use of nonblocking APIs.
* Table below shows the difference in python programming between using blocking
  and nonblocking APIs.

| PnetCDF Blocking APIs | PnetCDF Nonblocking APIs |
|:-------|:--------|
| ...<br># define 3 variables of NC_DOUBLE type ||
| psfc = f.createVariable("PSFC", "f8", ("time", "lat", "lon"))<br>prcp = f.createVariable("prcp", "f8", ("time", "lat", "lon"))<br>snow = f.createVariable("SNOW", "f8", ("time", "lat", "lon")) | ditto |
| ... ||
| # exit define mode and enter data mode<br>f.enddef() | ditto |
| ...<br># Call blocking APIs to write 3 variables to the file | <br># Call nonblocking APIs to post 3 write requests |
| psfc.put_var_all(psfc_buf, start, count)<br>prcp.put_var_all(prcp_buf, start, count)<br>snow.put_var_all(snow_buf, start, count)<br>| reqs = [0]*3<br>reqs[0] = psfc.iput_var(psfc_buf, start, count)<br>reqs[1] = prcp.iput_var(prcp_buf, start, count)<br>reqs[2] = snow.iput_var(snow_buf, start, count)|
| | # Wait for nonblocking APIs to complete<br>errs = [0]*3<br>f.wait_all(3, reqs, errs)|


