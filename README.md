# PnetCDF-python
![](https://img.shields.io/badge/python-v3.9-blue) ![](https://img.shields.io/badge/tests%20passed-49-brightgreen)

### Overview
PnetCDF-python is a Python interface to
[PnetCDF](https://parallel-netcdf.github.io/), a high-performance parallel I/O
library for accessing netCDF files.
This package allows Python users to access netCDF data using the rich ecosystem
of Python's scientific computing libraries, making it a valuable tool for
applications that require parallel access to netCDF files.

### Data objects in PnetCDF-python programming

At a granular level, PnetCDF-python is a library that consists of the following
components:

| Component | Description |
| ---- | --- |
| **File** |`pnetcdfpy.File` is a high-level object representing a netCDF file, which provides a Pythonic interface to create, read and write contents in an netCDF file. A File object serves as the root container for dimensions, variables, and attributes. Together they describe the structures of data objects and relations among them stored in a netCDF file. |
| **Attribute** | NetCDF attributes can be created, accessed, and manipulated using python dictionary-like syntax. A Pythonic interface for metadata operations is provided both in the `File` class (for global attributes) and the `Variable` class (for variable's attributes). |
| **Dimension** | Dimension defines the dimensional shape of variables. NetCDF variables are multidimensional arrays. The `Dimension` object, which is also a key component of `File` class, provides an interface to create, access and manipulate dimensions. |
| **Variable** | Variable is a core component of a netCDF file representing an array of data values organized along one or more dimensions. In addition to data types and dimensions, variables can be associated with attributes. The `Variable` object in the library provides operations to read and write the data and metadata of a variable stored in a netCDF file. Programming of PnetCDF is divided into `define` and `data` modes. New data objects can be created in the `define` mode. Reading and writings data objects are done in the `data` mode, which can be done through either explicit function-call style methods or indexer-style (numpy-like) syntax. |

### Software Dependencies
* Python 3.9 or above
* MPI libraries
* PnetCDF [C library](https://github.com/Parallel-netCDF/PnetCDF), built with shared libraries.
* Python library [mpi4py](https://mpi4py.readthedocs.io/en/stable/install.html)
* Python library [numpy](http://www.numpy.org/)

### Developer Installation
* Clone this GitHub repository
* Make sure the above dependent software are installed.
* In addition, [Cython](http://cython.org/) is required for developer installation.
* Set the environment variable `PNETCDF_DIR` to PnetCDF's installation path.
* Make sure utility program `pnetcdf-config` is available in `$PNETCDF_DIR/bin`.
* Run command below to install.
  ```
  CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir pip install .
  ```

### Current status of API Development
The project is under active development. [dev_status.md](docs/dev_status.md) shows
a summary of the current implementation status.


### Testing
* Run command below to test all the test programs available in folder `./test`,
  which will run 4 MPI processes for each test. The number of processes can be
  changed by setting the environment variable `NPROC` to a different number.
  ```sh
  ./test_all.sh [test_file_output_dir]
  ```
* To run a specific individual test, run command below
  ```sh
  mpiexec -n [num_process] python test/tst_program.py [test_file_output_dir]
  ```
* The optional `test_file_output_dir` argument enables the testing program to
  save out generated test files in the directory. The default is the current
  folder.
* Similarly, one can test all example programs in the folder `examples` by
  running commands below.
  ```sh
  cd examples
  ./test_all.sh [test_file_output_dir]
  ```


### Additional Resources
* [PnetCDF-python User Guide](https://pnetcdfpython.readthedocs.io/en/latest/)
* [Comparison between NetCDF4-python and PnetCDF-python](docs/nc4_vs_pnetcdf.md)
* [PnetCDF](https://parallel-netcdf.github.io/)

### Acknowledgements
Ongoing development and maintenance of PnetCDF-python is supported by the U.S. Department of Energy's Office of Science, Scientific Discovery through Advanced Computing (SciDAC) program, OASIS Institute.

