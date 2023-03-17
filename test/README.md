# PnetCDF-python unittest
This directory contains all unittest programs in python. A detailed description of each test and run instructions are provided at the beginning of each file. All tests are expected to run with multi-processing enabled by MPI. Most test programs automatically run test cases through all three supported file formats (CDF-1, CDF-2, and CDF-5)

### Run test programs
Make sure PnetCDF-python is installed and you are in the top directory
* To run all the existing tests, execute 

```sh
./test_all.csh [test_file_output_dir]
```

* To run a specific single test, execute 

```sh
mpiexec -n [num_process] python3 test/tst_program.py [test_file_output_dir]
```

The optional `test_file_dir` argument enables the testing program to save out generated test files in the directory

### Test program overview
* **tst_file** \
 This series of test programs is focused on file creation and access through the `File` constructor, particularly with respect to the following aspects:\
    * different access modes ("r+", "w", etc)
    * clobber option

* **tst_dims** \
 This series of tests is focused on dimension initialization, dimension methods, and their interactions with netCDF variables using the `File` object API. Particularly, these test program tests the following:\
    * `Dimension` object basic attributes and methods including name, length
    * interactions with netCDF variable
        * different syntax for referencing associated dimensions at defining variables step
        * unlimited dimension length changes after adding/removing variable data

* **tst_atts** \
 This series of tests is focused on manipulating attributes using the `File` object API (for global attributes) and the `Variable` object API (for variable attributes):\
    * define attributes of various data types with explicit methods or python-dictionary style syntax
    * attribute-based methods

* **tst_var**\
 This series of test programs writes data to or reads from variables within a netCDF file with different syntaxes and different access patterns using the `Variable` object interface. For data mode operations, both independent i/o and collective i/o are tested by default.\
    * **tst_var_indexer**: test reading from or writing data to netCDF variable using slicing or indexer (numpy-style) syntax
    * **tst_var_type**: test writing data of heterogeneous data types to the defined variable 
    * **tst_var_put**: this series of tests look into the process of writing data to a netCDF variable using explicit function-call style method concerning different needs of access patterns. Usually, each process is configured to write to a designated area within the netCDF variable.
    * **tst_var_get**: this series of tests is focused on reading data from a netCDF variable using explicit function-call style method with respect to different needs of access patterns. Usually, each process is configured to read from a designated area within the netCDF variable.


