![](https://img.shields.io/badge/python-v3.9-blue) ![](https://img.shields.io/badge/tests%20passed-49-brightgreen)

# PnetCDF-python
### Overview
PnetCDF-python is a Python interface to
[PnetCDF](https://parallel-netcdf.github.io/), a high-performance parallel I/O
library for accessing netCDF files.
This package allows Python users to access netCDF data using the rich ecosystem
of Python's scientific computing libraries, making it a valuable tool for
applications that require parallel access to netCDF files.

### More about PnetCDF-python

At a granular level, PnetCDF-python is a library that consists of the following
components:

| Component | Description |
| ---- | --- |
| **File** |`pncpy.File` is a high-level object representing a netCDF file, which provides a Pythonic interface to create, read and write contents in an netCDF file. A File object serves as the root container for dimensions, variables, and attributes. Together they describe the structures of data objects and relations among them stored in a netCDF file. |
| **Attribute** | NetCDF attributes can be created, accessed, and manipulated using python dictionary-like syntax. A Pythonic interface for metadata operations is provided both in the `File` class (for global attributes) and the `Variable` class (for variable's attributes). |
| **Dimension** | Dimension defines the dimensional shape of variables. NetCDF variables are multidimensional arrays. The `Dimension` object, which is also a key component of `File` class, provides an interface to create, access and manipulate dimensions. |
| **Variable** | Variable is a core component of a netCDF file representing an array of data values organized along one or more dimensions. In addition to data types and dimensions, variables can be associated with attributes. The `Variable` object in the library provides operations to read and write the data and metadata of a variable stored in a netCDF file. Programming of PnetCDF is divided into `define` and `data` modes. New data objects can be created in the `define` mode. Reading and writings data objects are done in the `data` mode, which can be done through either explicit function-call style methods or indexer-style (numpy-like) syntax. |

### Software Dependencies

* Python 3.9 or above
* MPI libraries
* PnetCDF [C library](https://github.com/Parallel-netCDF/PnetCDF)
* Python library [mpi4py](https://mpi4py.readthedocs.io/en/stable/install.html)
* Python library [numpy](http://www.numpy.org/)
* [Cython](http://cython.org/) for working with the in-development version

### Installation command

```sh
CC=/path/to/mpi/bin/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir/ pip install pncpy
```

### Development installation
* Clone this GitHub repository
* Make sure the dependent software listed above are installed, i.e. python,
  numpy, mpi4py, and Cython.
* Make sure a working MPI implementation and PnetCDF are built with
  shared libraries(`--enable-shared`),
  and their binaries, including `pnetcdf-config` utility program are includes
  in $PATH. (or specify `pnetcdf-config` filepath in `setup.cfg`)
* (Optional) create python virtual environment and activate it.
* Run `CC=mpicc PNETCDF_DIR=/path/to/pnetcdf/dir/ pip install -v .`

### Current status of API Development

The project is under active development. [dev_status.md](./dev_status.md) shows
a summary of the current implementation status.


### Testing
* To run all the existing tests, use command below.
```sh
./test_all.csh [test_file_output_dir]
```

* To run a specific individual test, run command below
```sh
mpiexec -n [num_process] python3 test/tst_program.py [test_file_output_dir]
```

The optional `test_file_output_dir` argument enables the testing program to
save out generated test files in the directory

### Additional Resources
* [PnetCDF-python User Guide](https://pnetcdf-python.readthedocs.io/en/latest/)
* [PnetCDF](https://parallel-netcdf.github.io/)

### Acknowledgements
Ongoing development and maintenance of PnetCDF-python is supported by the U.S. Department of Energy's Office of Science, Scientific Discovery through Advanced Computing (SciDAC) program, OASIS Institute.

