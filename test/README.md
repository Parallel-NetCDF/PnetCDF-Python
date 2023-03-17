# PnetCDF-python unittest
This directory contains all test programs in python. Detailed description of each test and run instructions are provided at the beginning of each file. All tests are expected to run with multi-processing enabled by MPI. Most test programs automatically run test cases through all three supported file formats (CDF-1, CDF-2 and CDF-5)

### Run test programs
Make sure PnetCDF-python is installed and you are in top directory
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
 This series of test programs is focused on file creation and access through the `File` constructor, particularly with repsect to the following aspects:\
    * different access modes ("r+", "w", etc)
    * clobber option

* **tst_dims** \
 This series of tests is focused on defining dimensions using the `File` object API, dimension methods and their interactions with netCDF variables. Particularly, these test program tests the following:\
    * `Dimension` object basic attributes and methods including name, length
    * interactions with netCDF variable
        * different syntax for referencing associated dimensions at defining variables step
        * unlimited dimension length changes after adding/removing variable data

* **tst_atts** \
 This series of test is focused on manipulating attributes using the `File` object API (for globale attributes) and the `Variable` object API (for variable attribute):\
    * define attributes of various data types with explicit methods or python-dictionary style syntax
    * attribute-based methods

* **tst_var**\
 This series of test programs writes data to or reads from variables within a netCDF file with different syntaxes and different access patterns using the `Variable` object interface. For data mode operations, both independent i/o and collective i/o are tested by default.\
    * **tst_var_indexer**: test reading from or writing data to netCDF variable using slicing or indexer (numpy-style) syntax
    * **tst_var_type**: test writing data of heterogeneous datatypes to defined variable 
    * **tst_var_put**: this series of tests look into the process of writing data to a netCDF variable using explicit function-call style method with respect to different needs of access pattern. Each method maps to the corresponding `ncmpi_put_var` function variant in C
    * **tst_var_get**: this series of tests is focused on reading data from a netCDF variable using explicit function-call style method with respect to different needs of access pattern. Each method maps to the corresponding `ncmpi_get_var` function variant in C


