# Comparison between PnetCDF-Python and NetCDF4-Python

Programming using [NetCDF4-Python](http://unidata.github.io/netcdf4-python/) and
[PnetCDF-Python](https://pnetcdf-python.readthedocs.io) are very similar.
Below lists some of the differences, including the file format support and
operational modes.

* [Supported File Formats](#supported-file-formats)
* [Differences in Python Programming](#differences-in-python-programming)
* [Define Mode and Data Mode](#define-mode-and-data-mode)
* [Collective and Independent I/O Mode](#collective-and-independent-io-mode)
* [Blocking vs. Nonblocking APIs](#blocking-vs-nonblocking-apis)

---

## Supported File Formats
* NetCDF4 supports both classic and HDF5-based file formats.
  + Classic file format (CDF-1) -- The ESDS Community Standard defined the file format
    to be used in the NetCDF user community in 1989. The file header bears a
    signature of character string 'CDF-1' and now is commonly referred to as
    [CDF-1](https://parallel-netcdf.github.io/doc/c-reference/pnetcdf-c/CDF_002d1-file-format-specification.html)
    file format.
    * 'CDF-2' format -- The CDF-1 format was later extended to support large
      file size (i.e.  larger than 2GB) in 2004. See its specification in
      [ESDS-RFC-011v2.0](https://cdn.earthdata.nasa.gov/conduit/upload/496/ESDS-RFC-011v2.00.pdf).
      Because its file header bears a signature of 'CDF-2' and the format is
      also commonly referred to as
      [CDF-2](https://parallel-netcdf.github.io/doc/c-reference/pnetcdf-c/CDF_002d2-file-format-specification.html)
      format.
    * [CDF-5](https://parallel-netcdf.github.io/doc/c-reference/pnetcdf-c/CDF_002d5-file-format-specification.html)
      format -- The CDF-2 format was extended by PnetCDF developer team
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
## Define Mode and Data Mode

In PnetCDF, an opened file is in either define mode or data mode. Switching
between the modes is done by explicitly calling `"pnetcdf.File.enddef()"` and
`"pnetcdf.File.redef()"`. NetCDF4-Python has no such mode switching
requirement. The reason of PnetCDF enforcing such a requirement is to ensure
the metadata consistency across all the MPI processes and keep the overhead of
metadata synchronization small.

* Define mode
  + When calling constructor of python class `"pnetcdf.File()"` to create a new
    file, the file is automatically put in the define mode.  While in the
    define mode, the python program can create new dimensions, i.e. instances
    of class `"pnetcdf.Dimension"`, new variables, i.e. instances of class
    `"pnetcdf.Variable"`, and netCDF attributes. Modification of these data
    objects' metadata can only be done when the file is in the define mode.
  + When opening an existing file, the opened file is automatically put in the
    data mode. To add or modify the metadata, a python program must call
    `"pnetcdf.File.redef()"`.

* Data mode
  + Once the creation or modification of metadata is complete, the python
    program must call `"pnetcdf.File.enddef()"` to leave the define mode and
    enter the data mode.
  + While an open file is in data mode, the python program can make read and
    write requests to that variables that have been created.

<ul>
  <li> A PnetCDF-Python example shows switching between define and data modes
       after creating a new file.</li>
  <li> <details>
  <summary>Example code fragment (click to expand)</summary>

```python
  import pnetcdf
  ...
  # Create the file
  f = pnetcdf.File(filename, 'w', "NC_64BIT_DATA", MPI.COMM_WORLD)
  ...
  # Define dimensions
  dim_y = f.def_dim("Y", 16)
  dim_x = f.def_dim("X", 32)

  # Define a 2D variable of integer type
  var = f.def_var("grid", pnetcdf.NC_INT, (dim_y, dim_x))

  # Add an attribute of string type to the variable
  var.str_att_name = "example attribute"

  # Exit the define mode
  f.enddef()

  # Write to a subarray of the variable, var
  var[4:8, 20:24] = buf

  # Re-enter the define mode
  f.redef()

  # Define a new 2D variable of float type
  var_flt = f.def_var("temperature", pnetcdf.NC_FLOAT, (dim_y, dim_x))

  # Exit the define mode
  f.enddef()

  # Write to a subarray of the variable, var_flt
  var_flt[0:4, 16:20] = buf_flt

  # Close the file
  f.close()
```
</details></li>

  <li> An example shows switching between define and data modes after opening an existing file.
  </li>
  <li> <details>
  <summary>Example code fragment (click to expand)</summary>

```python
  import pnetcdf
  ...
  # Opening an existing file
  f = pnetcdf.File(filename, 'r', MPI.COMM_WORLD)
  ...
  # get the python handler of variable named 'grid', a 2D variable of integer type
  var = f.variables['grid']

  # Read the variable's attribute named "str_att_name"
  str_att = var.str_att_name

  # Read a subarray of the variable, var
  r_buf = np.empty((4, 4), var.dtype)
  r_buf = var[4:8, 20:24]

  # Re-enter the define mode
  f.redef()

  # Define a new 2D variable of double type
  var_dbl = f.def_var("precipitation", pnetcdf.NC_DOUBLE, (dim_y, dim_x))

  # Add an attribute of string type to the variable
  var_dbl.unit = "mm/s"

  # Exit the define mode
  f.enddef()

  # Write to a subarray of the variable, var_dbl
  var_dbl[0:4, 16:20] = buf_dbl

  # Close the file
  f.close()
```
</details></li>
</ul>


---
## Collective and Independent I/O Mode

The terminology of collective and independent I/O comes from MPI standard. A
collective I/O function call requires all the MPI processes opening the same
file to participate. On the other hand, an independent I/O function can be
called by an MPI process independently from others.

For metadata I/O, both PnetCDF and NetCDF4 require the function calls to be
collective.

* Mode Switch Mechanism
  + PnetCDF-Python -- when a file is in the data mode, it can be put into
    either collective or independent I/O mode.  The default mode is collective
    I/O mode.  Switching to and exiting from the independent I/O mode is done
    by explicitly calling `"pnetcdf.File.begin_indep()"` and
    `"pnetcdf.File.end_indep()"`.

  + NetCDF4-Python -- collective and independent mode switching is done per
    variable basis. Switching mode is done by explicitly calling
    `"Variable.set_collective()"` before accessing the variable.
    For more information, see
    [NetCDF4-Python User Guide on Parallel I/O](https://unidata.github.io/netcdf4-python/#parallel-io)

<ul>
  <li> A PnetCDF-Python example shows switching between collective and
       independent I/O modes.</li>
  <li> <details>
  <summary>Example code fragment (click to expand)</summary>

```python
  import pnetcdf
  ...
  # Create the file
  f = pnetcdf.File(filename, 'w', "NC_64BIT_DATA", MPI.COMM_WORLD)
  ...
  # Metadata operations to define dimensions and variables
  ...
  # Exit the define mode (by default, into the collective I/O mode)
  f.enddef()

  # Write to variables collectively
  var_flt[start_y:end_y, start_x:end_x] = buf_flt
  var_dbl[start_y:end_y, start_x:end_x] = buf_dbl

  # Leaving collective I/O mode and entering independent I/O mode
  f.begin_indep()

  # Write to variables independently
  var_flt[start_y:end_y, start_x:end_x] = buf_flt
  var_dbl[start_y:end_y, start_x:end_x] = buf_dbl

  # Close the file
  f.close()
```
</details></li>
</ul>

<ul>
  <li> A NetCDF4-Python example shows switching between collective and
       independent I/O modes.</li>
  <li> <details>
  <summary>Example code fragment (click to expand)</summary>

```python
  import netCDF4
  ...
  # Create the file
  f = netCDF4.File(filename, 'w', "NC_64BIT_DATA", MPI.COMM_WORLD, parallel=True)
  ...
  # Metadata operations to define dimensions and variables
  ...

  # Write to variables collectively
  var_flt.set_collective(True)
  var_flt[start_y:end_y, start_x:end_x] = buf_flt

  var_dbl.set_collective(True)
  var_dbl[start_y:end_y, start_x:end_x] = buf_dbl

  # Write to variables independently
  var_flt.set_collective(False)
  var_flt[start_y:end_y, start_x:end_x] = buf_flt

  var_dbl.set_collective(False)
  var_dbl[start_y:end_y, start_x:end_x] = buf_dbl

  # Close the file
  f.close()
```
</details></li>
</ul>

---

## Blocking vs Nonblocking APIs
* Blocking APIs -- All NetCDF4 APIs are blocking APIs. A blocking API means the
  call to the API will not return until the operation is completed. For
  example, a call to `Variable.put_var()` will return only when the write data
  has been stored at the system space, e.g. file systems. Similarly, a call to
  `Variable.get_var()` will only return when the user read buffer containing
  the data retrieved from the file. Therefore, when a series of `put/get`
  blocking APIs are called, these calls will be committed by the NetCDF4
  library one at a time, following the same order of the calls.
* Nonblocking APIs -- In addition to blocking APIs, PnetCDF provides the
  nonblocking version of the APIs. A nonblocking API means the call to the API
  will return as soon as the `put/get` request has been registered in the
  PnetCDF library. The commitment of the request may happen later, when a call
  to `File.wait_all()/File.wait()` is made. The nonblocking APIs are listed
  below.
  + `Variable.iput_var()` - posts a nonblocking request to write to a variable.
  + `Variable.iget_var()` - posts a nonblocking request to from from a variable.
  + `Variable.bput_var()` - posts a nonblocking, buffered request to write to a variable.
  + `Variable.iput_varn()` - posts a nonblocking request to write multiple subarrays to a variable.
  + `Variable.iget_varn()` - posts a nonblocking request to read multiple subarrays from a variable.
  + `Variable.bput_varn()` - posts a nonblocking, buffered request to write multiple subarrays to a variable.
  + `File.wait_all()` - waits for nonblocking requests to complete, using collective MPI-IO.
  + `File.wait()` - waits for nonblocking requests to complete, using independent MPI-IO.
  + `File.attach_buff()` - Let PnetCDF to allocate an internal buffer to cache bput write requests.
  + `File.detach_buff()` - Free the attached buffer.
* The advantage of using nonblocking APIs is when there are many small
  `put/get` requests and each of them has a small amount.  PnetCDF tries to
  aggregate and coalesce multiple registered nonblocking requests into a large
  one, because I/O usually performs better when the request amounts are large
  and contiguous. See example programs
  [nonblocking_write.py](../examples/nonblocking/nonblocking_write.py) and
  [nonblocking_read.py](../examples/nonblocking/nonblocking_read.py).
* Table below shows the difference in python programming between using blocking
  and nonblocking APIs.

| PnetCDF Blocking APIs   PnetCDF Nonblocking APIs |
|:-------|:--------|
| ...<br># define 3 variables of NC_DOUBLE type ||
| psfc = f.createVariable("PSFC", "f8", ("time", "lat", "lon"))<br>prcp = f.createVariable("PRCP", "f8", ("time", "lat", "lon"))<br>snow = f.createVariable("SNOW", "f8", ("time", "lat", "lon")) | ditto |
| ... ||
| # exit define mode and enter data mode<br>f.enddef() | ditto |
| ...<br># Call blocking APIs to write 3 variables to the file | <br># Call nonblocking APIs to post 3 write requests |
| psfc.put_var_all(psfc_buf, start, count)<br>prcp.put_var_all(prcp_buf, start, count)<br>snow.put_var_all(snow_buf, start, count)<br>| reqs = [0]*3<br>reqs[0] = psfc.iput_var(psfc_buf, start, count)<br>reqs[1] = prcp.iput_var(prcp_buf, start, count)<br>reqs[2] = snow.iput_var(snow_buf, start, count)|
| | # Wait for nonblocking APIs to complete<br>errs = [0]*3<br>f.wait_all(3, reqs, errs)|


