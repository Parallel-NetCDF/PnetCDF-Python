![](https://img.shields.io/badge/python-v3.9-blue) ![](https://img.shields.io/badge/tests%20passed-48-brightgreen)

# PnetCDF-python
### Overview
PnetCDF-python is a [Python](http://python.org)/[numpy](http://numpy.org) interface to the PnetCDF, a high-performance parallel I/O library for accessing netCDF files. This integration with Python allows for easy manipulation, analysis, and visualization of netCDF data using the rich ecosystem of Python scientific computing libraries, making it a valuable tool for python-based applications that requires high-performance access to netCDF files. 
### More about PnetCDF-python

At a granular level, PnetCDF-python is a library that consists of the following components:

| Component | Description |
| ---- | --- |
| **File** |`pncpy.File` is a high-level object representing an netCDF file, which provides a Pythonic interface to create, read and write within an netCDF file. A File object serve as the root container for dimensions, variables and attributes. Together they describe the meaning of data and relations among data fields stored in a netCDF file. |
| **Attribute** | In the library, netCDF attributes can be created, accessed, and manipulated using python dictionary-like syntax. A Pythonic interface for metadata operations is provided both in the `File` class (for global attributes) and the `Variable` class (for variable attributes). |
| **Dimension** | Dimensions define the shape and structure of variables and store coordinate data for multidimensional arrays. The `Dimension` object, which is also a key component of `File` object, provides an interface to create, access and manipulate dimensions. |
| **Variable** | Variable is a core component of a netCDF file representing an array of data values organized along one or more dimensions, with associated metadata in the form of attributes. The `Variable` object in the library provides define and data operations to read and write the data and metadata of a variable within a netCDF file. Particularly, data operationa have a flexible interface, where reads and writes can be done through either explicit function-call style methods or indexer-style (numpy-like) syntax. |

### Dependencies
* Python 3.9 or above
* PnetCDF [C library](https://github.com/Parallel-netCDF/PnetCDF) built with shared libraries
* Python libraries [mpi4py](https://mpi4py.readthedocs.io/en/stable/install.html), [numpy](http://www.numpy.org/)
* To work with the in-development version, you need to install [Cython](http://cython.org/)

### Development installation
* Clone GitHub repository 

* Make sure [numpy](http://www.numpy.org/), [mpi4py](https://mpi4py.readthedocs.io/en/stable/install.html) and [Cython](http://cython.org/) are installed and you have [Python](https://www.python.org) 3.9 or newer.

* Make sure [PnetCDF](https://github.com/Parallel-netCDF/PnetCDF) are installed with shared library (`--enable-shared`), 
  and pnetcdf-config utility is in your Unix $PATH. (or specifiy the filepath of `pnetcdf-config` filepath in `setup.cfg`)

* (Optional) create python venv virtual environment and activate it

* Run `env CC=mpicc python3 setup.py build`, then `env CC=mpicc python3 setup.py install`

### Current build status
The project is under active development. Below is a summary of the current implementation status

#### Implemented
* netCDF File operations
* Dimension operations
* Attribute operations
* Variable define operations

#### Partially implemented
* Variable blocking mode data operations (90% completed)
    

#### Planned
* Variable non-blocking mode data operations


### Testing
* To run all the existing tests, execute 

```sh
./test_all.csh [test_file_output_dir]
```

* To run a specific single test, execute 

```sh
mpiexec -n [number of process] python3 test/tst_program.py [test_file_output_dir]
```

The optional `test_file_dir` argument enables test program to save out generated test files in the directory

### Resources
* [PnetCDF Overview][https://parallel-netcdf.github.io/]
* [Source code][https://github.com/Jonathanlyj/PnetCDF-Python]

### License