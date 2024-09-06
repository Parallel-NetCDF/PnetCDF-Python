# PnetCDF python
![](https://img.shields.io/badge/python-v3.9-blue)
![](https://img.shields.io/badge/tests%20passed-49-brightgreen)
![](https://readthedocs.org/projects/pnetcdf-python/badge/?version=latest)

PnetCDF-python is a Python interface to
[PnetCDF](https://parallel-netcdf.github.io/), a high-performance parallel I/O
library for accessing netCDF files.
This package allows Python users to access netCDF data using the rich ecosystem
of Python's scientific computing libraries, making it a valuable tool for
applications that require parallel access to netCDF files.

### Software Dependencies
* Python 3.9 or above
* MPI libraries
* PnetCDF [C library](https://github.com/Parallel-netCDF/PnetCDF), built with shared libraries.
* Python library [mpi4py](https://mpi4py.readthedocs.io/en/stable/install.html)
* Python library [numpy](http://www.numpy.org/)

### Developer Installation
* Clone this GitHub repository
* Make sure the above dependent software are installed.
* In addition, [Cython](http://cython.org/), [packaging](https://pypi.org/project/packaging/), [setuptools>=65](https://pypi.org/project/setuptools/) and [wheel](https://pypi.org/project/wheel/) are required for developer installation.
* Set the environment variable `PNETCDF_DIR` to PnetCDF's installation path.
* Make sure utility program `pnetcdf-config` is available in `$PNETCDF_DIR/bin`.
* Run command below to install.
  ```
  CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir pip install --no-build-isolation -e .
  ```
* Testing
  + Run command `"make check"` to test all the programs available in folders
    ["test/"](./test) and ["examples/"](./examples) in parallel on 4 MPI
    processes.
  + In addition, command `"make ptests"` runs the same tests using 3, 4, and 8
    MPI processes.

### Additional Resources
* PnetCDF-python [User Guide](https://pnetcdf-python.readthedocs.io/en/latest)
* [Data objects](docs/pnetcdf_objects.md) in PnetCDF python programming
* [Comparison](docs/nc4_vs_pnetcdf.md) of NetCDF4-python and PnetCDF-python
* [PnetCDF project home page](https://parallel-netcdf.github.io)
* [PnetCDF repository of C/Fortran library](https://github.com/Parallel-NetCDF/PnetCDF)

### Developer Team
* Youjia Li <<youjia@northwestern.edu>>
* Wei-keng Liao <<wkliao@northwestern.edu>> (Principle Investigator)

### Acknowledgements
Ongoing development and maintenance of PnetCDF-python is supported by the U.S.
Department of Energy's Office of Science, Scientific Discovery through Advanced
Computing (SciDAC) program, RAPIDS/OASIS Institute.

