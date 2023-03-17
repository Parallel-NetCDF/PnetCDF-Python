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
| Implemented | Partially implemented | Planned |
| ---- | --- | --- | 
| File operations API,<br />Dimension operations API,<br />Attribute operations API,<br />Variable define mode operations API| Variable data mode blocking operations (90% completed) | Variable data mode non-blocking operations| 



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