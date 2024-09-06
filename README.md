# PnetCDF for Python
![](https://img.shields.io/badge/python-v3.9-blue)
![](https://img.shields.io/badge/tests%20passed-49-brightgreen)
![](https://readthedocs.org/projects/pnetcdf-python/badge/?version=latest)

PnetCDF-Python is a Python interface to
[PnetCDF](https://parallel-netcdf.github.io/), a high-performance I/O library
for accessing netCDF files in parallel. It can provide MPI-based parallel
python programs to achieve a scalable I/O performance.

### Software Dependencies
* Python 3.9 or later.
* [numpy](http://www.numpy.org/) Python package.
* MPI C library and Python package, [mpi4py](https://mpi4py.readthedocs.io/en/stable/install.html).
* [PnetCDF C library](https://github.com/Parallel-netCDF/PnetCDF), built with shared libraries.

### Developer Installation
* Clone this GitHub repository
* Required software for developer installation:
  + The above mentioned dependent software are installed and additionally,
  + [Cython](http://cython.org/), [packaging](https://pypi.org/project/packaging/), [setuptools>=65](https://pypi.org/project/setuptools/) and [wheel](https://pypi.org/project/wheel/).
* Commands to install.
  ```
  export CC=/path/to/mpicc
  export PNETCDF_DIR=/path/to/pnetcdf/dir
  pip install --no-build-isolation -e .
  ```
* Testing -- Command `"make check"` tests all the programs available in folders
  ["test/"](./test) and ["examples/"](./examples).

### Additional Resources
* [Example programs](./examples#pnetcdf-python-examples) are available in
  folder `./examples`.
* PnetCDF-python [User Guide](https://pnetcdf-python.readthedocs.io/en/latest)
* [Data objects](docs/pnetcdf_objects.md) in PnetCDF python programming
* [Comparison](docs/nc4_vs_pnetcdf.md) of NetCDF4-python and PnetCDF-python
* [PnetCDF project home page](https://parallel-netcdf.github.io)
* [PnetCDF of C/Fortran library repository](https://github.com/Parallel-NetCDF/PnetCDF)

### Developer Team
* Youjia Li <<youjia@northwestern.edu>>
* Wei-keng Liao <<wkliao@northwestern.edu>>

### Acknowledgements
Ongoing development and maintenance of PnetCDF-python is supported by the U.S.
Department of Energy's Office of Science, Scientific Discovery through Advanced
Computing (SciDAC) program, RAPIDS/OASIS Institute.

