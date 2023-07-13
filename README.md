![](https://img.shields.io/badge/python-v3.9-blue) ![](https://img.shields.io/badge/tests%20passed-48-brightgreen)

# PnetCDF-python
### Overview
PnetCDF-python is a Python interface to PnetCDF, a high-performance parallel I/O library for accessing netCDF files. This integration with Python allows for easy manipulation, analysis, and visualization of netCDF data using the rich ecosystem of Python's scientific computing libraries, making it a valuable tool for python-based applications that require high-performance access to netCDF files. 
### More about PnetCDF-python

At a granular level, PnetCDF-python is a library that consists of the following components:

| Component | Description |
| ---- | --- |
| **File** |`pncpy.File` is a high-level object representing an netCDF file, which provides a Pythonic interface to create, read and write within an netCDF file. A File object serves as the root container for dimensions, variables, and attributes. Together they describe the meaning of data and relations among data fields stored in a netCDF file. |
| **Attribute** | In the library, netCDF attributes can be created, accessed, and manipulated using python dictionary-like syntax. A Pythonic interface for metadata operations is provided both in the `File` class (for global attributes) and the `Variable` class (for variable attributes). |
| **Dimension** | Dimension defines the shape and structure of variables and stores coordinate data for multidimensional arrays. The `Dimension` object, which is also a key component of `File` class, provides an interface to create, access and manipulate dimensions. |
| **Variable** | Variable is a core component of a netCDF file representing an array of data values organized along one or more dimensions, with associated metadata in the form of attributes. The `Variable` object in the library provides operations to read and write the data and metadata of a variable within a netCDF file. Particularly, data mode operations have a flexible interface, where reads and writes can be done through either explicit function-call style methods or indexer-style (numpy-like) syntax. |

### Dependencies
* Python 3.9 or above
* PnetCDF [C library](https://github.com/Parallel-netCDF/PnetCDF)
* Python libraries [mpi4py](https://mpi4py.readthedocs.io/en/stable/install.html), [numpy](http://www.numpy.org/)
* To work with the in-development version, you need to install [Cython](http://cython.org/)

### Development installation
* Clone GitHub repository 

* Make sure [numpy](http://www.numpy.org/), [mpi4py](https://mpi4py.readthedocs.io/en/stable/install.html) and [Cython](http://cython.org/) are installed and you have [Python](https://www.python.org) 3.9 or newer.

* Make sure [PnetCDF C](https://github.com/Parallel-netCDF/PnetCDF) is installed with shared libraries(`--enable-shared`), 
  and pnetcdf-config utility is in your Unix $PATH. (or specifiy `pnetcdf-config` filepath in `setup.cfg`)

* (Optional) create python virtual environment and activate it

* Run `env CC=mpicc python3 setup.py build`, then `env CC=mpicc python3 setup.py install`

### Current build status
The project is under active development. Below is a summary of the current implementation status
<!-- * **Implemented:** netCDF file operations API, dimension operations API, attribute operations API, variable define mode operations
* **Partially implemented:** variable blocking mode data operations (90% completed)
* **Planned:** variable non-blocking mode data operations -->
| Component | Implemented | To be implemented next (w/ priority\*) |
| ---- | --- | --- |
|File API| ncmpi_strerror<br />ncmpi_strerrno<br />ncmpi_create<br />ncmpi_open/close<br />ncmpi_enddef/redef<br />ncmpi_sync<br />ncmpi_begin/end_indep_data<br />ncmpi_inq_path <br />ncmpi_inq<br />ncmpi_wait<br />ncmpi_wait_all<br />ncmpi_inq_nreqs <br />ncmpi_inq_buffer_usage/size <br />ncmpi_cancel <br />ncmpi_set_fill <br />ncmpi_set_default_format <br />ncmpi_inq_file_info<br />ncmpi_inq_put/get_size <br />|  ncmpi_inq_libvers 2<br /> ncmpi_delete 2<br /> ncmpi_sync_numrecs 2<br /> ncmpi__enddef 2<br />  ncmpi_abort 3<br />ncmpi_inq_files_opened 2<br /> ncmpi_inq 3<br />|
|Dimension API|ncmpi_def_dim<br />ncmpi_inq_ndims<br />ncmpi_inq_dimlen<br />ncmpi_inq_dim<br />ncmpi_inq_dimname<br />ncmpi_rename_dim<br />| |
|Attribute API| ncmpi_put/get_att_text<br />ncmpi_put/get_att<br />ncmpi_inq_att<br />ncmpi_inq_natts<br />ncmpi_inq_attname<br />ncmpi_rename_att<br />ncmpi_del_att|ncmpi_copy_att 2<br />|
|Variable API| ncmpi_def_var<br />ncmpi_def_var_fill<br />ncmpi_inq_varndims<br />ncmpi_inq_varname<br />ncmpi_put/get_vara<br />ncmpi_put/get_vars<br />ncmpi_put/get_var1<br />ncmpi_put/get_var<br />ncmpi_put/get_varn<br />ncmpi_put/get_varm<br /> ncmpi_put/get_vara_all<br />ncmpi_put/get_vars_all<br />ncmpi_put/get_var1_all<br />ncmpi_put/get_var_all<br />ncmpi_put/get_varn_all<br />ncmpi_put/get_varm_all<br />ncmpi_iput/iget_var<br />ncmpi_iput/iget_vara<br />ncmpi_iput/iget_var1<br />ncmpi_iput/iget_vars<br />ncmpi_iput/iget_varm<br /> ncmpi_iput/iget_varn<br /> ncmpi_bput_var<br />ncmpi_bput_var1<br />ncmpi_bput_vara<br />ncmpi_bput_vars<br />ncmpi_bput_varm<br />ncmpi_bput_varn<br />ncmpi_fill_var_rec<br />|All type-specific put/get functions 3 <br /> (e.g. ncmpi_put_var1_double_all)<br /><br />All put/get_vard functions 3<br /><br />All mput/mget_var functions 3|
|Inquiry API|ncmpi_inq<br />ncmpi_inq_ndims<br />ncmpi_inq_dimname<br />ncmpi_inq_varnatts<br />ncmpi_inq_nvars<br />ncmpi_inq_vardimid<br />ncmpi_inq_var_fill<br />ncmpi_inq_buffer_usage<br />ncmpi_inq_buffer_size<br />ncmpi_inq_natts<br /> ncmpi_inq_malloc_max_size<br />ncmpi_inq_malloc_size<br />ncmpi_inq_format <br />ncmpi_inq_file_format<br />ncmpi_inq_num_rec_vars<br />ncmpi_inq_num_fix_vars<br />ncmpi_inq_unlimdim<br />ncmpi_inq_varnatts<br />ncmpi_inq_varndims<br />ncmpi_inq_varname<br />ncmpi_inq_vartype<br />ncmpi_inq_varoffset<br />ncmpi_inq_header_size<br />ncmpi_inq_header_extent<br />ncmpi_inq_recsize <br />ncmpi_inq_version<br />ncmpi_inq_striping<br />|ncmpi_inq_dimid 3<br />ncmpi_inq_dim 3<br />ncmpi_inq_malloc_list 2<br /> ncmpi_inq_var 3<br /> ncmpi_inq_varid 3<br />|
<p>\*priority level 1/2/3 maps to first/second/third priority</p>

<!-- |File operations API|,<br />Dimension operations API,<br />Attribute operations API,<br />Variable define mode operations API| Variable data mode blocking operations (90% completed) | Variable data mode non-blocking operations|  -->



### Testing
* To run all the existing tests, execute 

```sh
./test_all.csh [test_file_output_dir]
```

* To run a specific single test, execute 

```sh
mpiexec -n [num_process] python3 test/tst_program.py [test_file_output_dir]
```

The optional `test_file_output_dir` argument enables the testing program to save out generated test files in the directory

### Resources
* [PnetCDF Overview](https://parallel-netcdf.github.io/)
* [Source code](https://github.com/Jonathanlyj/PnetCDF-Python)

### License