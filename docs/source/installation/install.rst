============================================
Install from Source
============================================

Software Requirements
=====================

- PnetCDF C library
- Python 3.9 or later
- Python libraries: numpy, mpi4py
- Python libraries: Cython, setuptools (optional, for building from source)

Building PnetCDF C library
==========================

.. code-block:: bash

    # download PnetCDF C library v1.12.3 (or later)
    $ wget https://parallel-netcdf.github.io/Release/pnetcdf-1.12.3.tar.gz
    
    $ tar -xf pnetcdf-1.12.3.tar.gz
    $ cd pnetcdf-1.12.3

    # configure
    $ ./configure --prefix=/path/to/install-dir --enable-shared CC=mpicc
    
    # build and install
    $ make
    $ make install

Building PnetCDF-python from source
===================================

.. code-block:: bash

    # activate an virtual environment (optional)
    # use Python 3.9 or later
    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install --upgrade pip

    # install Python libraries
    $ pip install numpy Cython setuptools
    $ env CC=mpicc pip install --no-cache-dir mpi4py

    # download PnetCDF-python source code
    $ git clone git@github.com:yzanhua/pnetcdf-python.git
    $ cd pnetcdf-python

    # install PnetCDF-python
    env CC=mpicc python3 setup.py build
    env CC=mpicc python3 setup.py install


