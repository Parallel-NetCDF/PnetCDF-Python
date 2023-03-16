![](https://img.shields.io/badge/python-v3.9-blue) ![](https://img.shields.io/badge/tests%20passed-48-brightgreen)

# PnetCDF-python
### Overview
PnetCDF-python is a [Python](http://python.org)/[numpy](http://numpy.org) interface to the PnetCDF, a high-performance parallel I/O library for accessing NetCDF files. The python library is implemented on top of PnetCDF [C library](https://github.com/Parallel-NetCDF/PnetCDF) and MPI 
### Dependencies
* Python 3.9 or above
* PnetCDF [C library](https://github.com/Parallel-NetCDF/PnetCDF) built with shared libraries
* Python libraries [mpi4py](https://mpi4py.readthedocs.io/en/stable/install.html), [numpy](http://www.numpy.org/)
* To work with the in-development version, you need to install [Cython](http://cython.org/)

### Development installation
* Clone GitHub repository 

* Make sure [numpy](http://www.numpy.org/), [mpi4py](https://mpi4py.readthedocs.io/en/stable/install.html) and [Cython](http://cython.org/) are installed and you have [Python](https://www.python.org) 3.9 or newer.

* Make sure [PnetCDF](https://github.com/Parallel-NetCDF/PnetCDF) are installed with shared library (`--enable-shared`), 
  and pnetcdf-config utility is in your Unix $PATH. (or specifiy the filepath of `pnetcdf-config` filepath in `setup.cfg`)

* (Optional) create python venv virtual environment and activate it

* Run `env CC=mpicc python3 setup.py build`, then `env CC=mpicc python3 setup.py install`

### Current build status
The project is under active development. Below is a summary of the current implementation status

#### Implemented
* NetCDF File operations
* Dimension operations
* Attribute operations
* Variable define mode operations

#### Partially implemented
* Variable data mode operations
    * Blocking mode 

#### Planned
* Variable data mode operations
    * Non-blocking mode 

### Testing
* To run all the existing tests, execute 

```sh
./test_all.csh [test_file_output_dir]
```

* To run a specific single test, execute 

```sh
mpiexec -n [number of process] python3 test/test_progrm.py [test_file_output_dir]
```

With the optional test_file_dir argument test programs will save out generated test files in the directory

### Websites
* [PnetCDF Overview][https://parallel-netcdf.github.io/]
* [Source code][https://github.com/Jonathanlyj/PnetCDF-Python]