# Pnetcdf-python
## Setup
### Requirements
* Python 3.9+

## Development installation
* Clone GitHub repository 

* Make sure [numpy](http://www.numpy.org/), [mpi4py](https://mpi4py.readthedocs.io/en/stable/install.html) and [Cython](http://cython.org/) are installed and you have [Python](https://www.python.org) 3.9 or newer.

* Make sure [PnetCDF](https://github.com/Parallel-NetCDF/PnetCDF) are installed, 
  and pnetcdf-config is in $PATH. (or specifiy the filepath of `pnetcdf-config` filepath in `setup.cfg`)

* (Optional)create python venv virtual environment and activate it
* Run `env CC=mpicc python3 setup.py build`, then `env CC=mpicc python3 setup.py install`

## Development tasks
- [] Generic tasks
    - [x] The implementation Cython file (.pyx) splitted by classes(e.g. _File.pyx, Dimension.pyx)
    - [x] Add utils Cython files to include all helper functions and import them in class implementation files
    - [x] Fix "not found" error with direct importing pncpy module
    - [x] Provide more ways of locating pnetcdf_config in directories
    - [x] Verify that PnetCDF c functions are genuinely called during running 
    - [x] Add nc file validation step to test programs using pnetcdf CLI 
    - [x] Able to implement python constants that mapped to corresponding c constants
    - [ ] Fix segmentation error when raising runtime error

- [x] File API implementation
    - [x] Implement and test basic class instructor and attributes
    - [x] Implement and test Cmode and data format option 
    - [x] Implement inquiry functions related to file and dimension
    - [x] Implement and test methods to enter/exit define mode 
    - [x] Implement and test dimension operation methods
    - [x] Implement and test (global) attribute operation methods
    - [x] Implment and test variable operation methods

- [x] Dimension API implementation
    - [x] Implement and test dimension class constructor
    - [ ] Comprehensively test all dimension methods

- [x] Attribute API implmentation
    - [x] Global attribute methods under File class
    - [x] Variable attribute methods under Variable class
    - [ ] Comprehensively test all dimension methods

- [ ] Variable API implementation
    - [x] Implement and test basic class instructor and attributes
    - [x] Implement and test variable define operations
    - [x] Blocking mode 
        - [x] Import MPI datatype in the implementation
        - [x] Implement and test varaible data numpy-fassion write/read methods (collective & independent)
        - [x] Implement and test put/get_var1 methods (collective & independent)
        - [x] Implement and test put/get_var methods (collective & independent)
        - [x] Implement and test put/get_vara methods (collective & independent)
        - [x] Implement and test put/get_vars methods (collective & independent)
        - [ ] Implement and test put/get_varn methods (collective & independent)
        - [ ] Implement and test put/get_varm methods (collective & independent)
    - [ ] Non-blocking mode
## Common errors and solutions

| Error Msg      | Quick fix |
| ----------- | ----------- |
| Cannot use python variable/function without gil | Caused by undeclared c function; Added the declaration of C function in PnetCDF.pxi |
| Seg error on `PyArray_SIZE` | Add import_array() in a new line |
|NetCDF: Attribute not found| The method being called is not implemented|
    
## Design features
- Cython implmentation file (.pyx) partitioned by class. Each class has a seperate declaration file and implementation file
- In the case of CDF2-file, data types supported by CDF5 only will cause program to error out (no implicit datatype conversion)
- User need to explictly call File method to enter/exit define mode and independdent data mode






## References and learning materials
- [Python C extension build tutorial][https://realpython.com/build-python-c-extension-module]
- [Cython basics][https://cython.readthedocs.io/en/latest/src/userguide/language_basics.html]
- [netCDF4 - Python repo][https://github.com/Unidata/netcdf4-python]
- [h5py repo][https://github.com/h5py/h5py]
- [Disutils setupscript][https://docs.python.org/3/distutils/setupscript.html]
- [Disutils example][https://docs.python.org/3/distutils/examples.html]
- PyArray (extend numpy to c/c+) [https://numpy.org/doc/stable/user/c-info.how-to-extend.html#getting-at-ndarray-memory-and-accessing-elements-of-the-ndarray]