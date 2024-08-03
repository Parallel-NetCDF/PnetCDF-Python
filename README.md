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
* In addition, [Cython](http://cython.org/), [packaging](https://pypi.org/project/packaging/) and ['wheel'](https://pypi.org/project/wheel/) are required for developer installation.
* Set the environment variable `PNETCDF_DIR` to PnetCDF's installation path.
* Make sure utility program `pnetcdf-config` is available in `$PNETCDF_DIR/bin`.
* Run command below to install.
  ```
  CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir pip install --no-build-isolation -e .
  ```
* Testing
  + Run command below to test all the test programs available in folder
    `./test`, which will run 4 MPI processes for each test. The number of
    processes can be changed by setting the environment variable `NPROC` to a
    different number.
    ```sh
    ./test_all.sh [test_file_output_dir]
    ```
  + To run a specific individual test, run command below
    ```sh
    mpiexec -n [num_process] python test/tst_program.py [test_file_output_dir]
    ```
    * The optional `test_file_output_dir` argument enables the testing program
      to save out generated test files in the directory. The default is the
      current folder.
  + Similarly, one can test all example programs in the folder `examples` by
    running commands below.
    ```sh
    cd examples
    ./test_all.sh [test_file_output_dir]
    ```

### Additional Resources
* [PnetCDF-python User Guide](https://pnetcdf-python.readthedocs.io/en/latest/)
* [Data objects in PnetCDF python programming](docs/pnetcdf_objects.md)
* [Comparison between NetCDF4-python and PnetCDF-python](docs/nc4_vs_pnetcdf.md)
* This project is under active development. The current status of API
  implementation can be found in [dev_status.md](docs/dev_status.md).
* [PnetCDF](https://parallel-netcdf.github.io/)

### Acknowledgements
Ongoing development and maintenance of PnetCDF-python is supported by the U.S.
Department of Energy's Office of Science, Scientific Discovery through Advanced
Computing (SciDAC) program, OASIS Institute.

