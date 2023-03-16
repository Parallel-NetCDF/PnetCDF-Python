# PnetCDF-python unittest
This directory contains all test programs in python. Detailed description of each test and run instructions are provided at the beginning of each file. All tests are expected to run with multi-prcoessing enabled by MPI. Most test programs automatically checks tests on all three file formates (CDF-1, CDF-2 and CDF-3)

* **tst_files** \
 This series of test programs focuses on file creation and access through the `File` constructor, particularly with repsect to the following aspects:\
    * Different access modes ("r+", "w", etc)
    * Clobber option

* **tst_dims** \
 This series of test programs focuses on defining dimensions using the `File` object API, dimension methods and their interactions with netCDF variables. Particularly, these test program tests the following:\
    * `Dimension` object basic attributes and methods including name, length
    * Interactions with netCDF variable
        * Different syntax for referencing associated dimensions at defineVariable step
        * Unlimited dimension length changes after adding/removing variable data

* **tst_atts** \
 This series of test programs focuses on manipulating attributes using the `File` object API (for globale attributes) and the `Variable` object API (for variable attribute):\
    * Define attributes of various data types with explicit methods or python-dictionary style syntax
    * Attribute-based methods

* **tst_var**\
 This series of test programs writes data to or reads from variables within a netCDF file with different syntaxes and different access patterns using the `Variable` object interface. For data mode operations, both independent i/o and collective i/o are tested by default.\
    * **tst_var_indexer**: test reading from or writing data to netCDF variable using slicing or indexer (numpy-style) index
    * **tst_var_type**: particulay test writing data of heterogeneous datatypes to defined variable 
    * **tst_var_put**: this series of test programs test writing data to a netCDF variable using explicit function-call style method with respect to different needs of access pattern. Each method maps to the corresponding `ncmpi_put_var` function variant in C
    * **tst_var_get**: this series of test programs test reading data from a netCDF variable using explicit function-call style method with respect to different needs of access pattern. Each method maps to the corresponding `ncmpi_get_var` function variant in C
