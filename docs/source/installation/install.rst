===================================
Installation 
===================================


Quick Install
===================================

Quick installation via pip install is currently unavailable as this library has not yet been uploaded to PyPI. 
Please follow building from source instructions provided below to set up the library.

Install from Source
============================================

Software Requirements
 - PnetCDF C library
 - Python 3.9 or later
 - Python libraries: numpy, mpi4py
 - Python libraries: Cython, setuptools (optional, for building from source)

Building PnetCDF C library
 .. code-block:: bash

     # download PnetCDF C library v1.12.3 (or later)
     $ wget https://parallel-netcdf.github.io/Release/pnetcdf-1.12.3.tar.gz
    
     $ tar -xf pnetcdf-1.12.3.tar.gz
     $ cd pnetcdf-1.12.3

     # configure
     $ ./configure --prefix=/path/to/install-dir --enable-shared --disable-fortran --disable-cxx CC=mpicc 
    
     # build and install
     $ make
     $ make install

Building PnetCDF-python from source
 .. code-block:: bash

     # activate an virtual environment (optional)
     # use Python 3.9 or later
     $ python -m venv env
     $ source env/bin/activate
     $ pip install --upgrade pip setuptools wheel packaging

     # install Python libraries
     $ pip install numpy Cython
     $ env CC=/path/to/mpicc pip install mpi4py

     # download PnetCDF-python source code
     $ git clone git@github.com:Parallel-NetCDF/PnetCDF-Python.git
     $ cd PnetCDF-Python

     # install PnetCDF-python
     env CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir/ pip install --no-build-isolation -e .
