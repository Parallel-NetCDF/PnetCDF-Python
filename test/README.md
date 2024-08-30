# PnetCDF-python unit tests

This directory contains unit test programs in python. Detailed description of
each test and run instructions are provided at the beginning of each file. All
tests are expected to run with multiple MPI processes.

---
### Running individual test programs

Make sure PnetCDF-python and all its dependent packages are installed first.
Please refer to [../README.](../README.md) in the top directory for
installation information.

* Use mpiexec command to run individual test programs. For example, command
  line below run `tst_file_mode.py` on 4 MPI processes.
  ```sh
  mpiexec -n 4 python tst_file_mode.py [file_output_dir]
  ```
* The optional argument `file_output_dir` enables the testing program to save
  the generated output files in the specified directory. Default is the current
  directory.

---
### Overview of Test Programs

* **tst_file**
  + This series of test programs is focused on file creation and access through the
    `File` constructor, particularly with respect to the following aspects:
    * different access modes ("r+", "w", etc)
    * clobber option

* **tst_dims**
  + This series of tests is focused on dimension initialization, dimension
    methods, and their interactions with netCDF variables using the `File`
    object API. Particularly, these test program tests the following:
    * `Dimension` object basic attributes and methods including name, length
    * interactions with netCDF variable
        + different syntax for referencing associated dimensions at defining variables step
        + unlimited dimension length changes after adding/removing variable data

* **tst_atts**
  + This series of tests is focused on manipulating attributes using the `File`
    object API (for global attributes) and the `Variable` object API (for
    variable attributes):
    * define attributes of various data types with explicit methods or
      python-dictionary style syntax
    * attribute-based methods

* **tst_var**
  + This series of test programs writes data to or reads from variables within
    a netCDF file with different syntaxes and different access patterns using
    the `Variable` object interface. For data mode operations, both independent
    I/O and collective I/O are tested by default.

  + **tst_var_indexer**
    * Reading from or writing data to netCDF variable using slicing or indexer
      (numpy-style) syntax

  + **tst_var_type**
    * Writing data of heterogeneous data types to the defined variable

  + **tst_var_put**
    * This series of tests look into the process of writing data to a netCDF
      variable using explicit function-call style method concerning different
      needs of access patterns. Usually, each process is configured to write to
      a designated area within the netCDF variable.

  + **tst_var_get**
    * This series of tests is focused on reading data from a netCDF variable
      using explicit function-call style method with respect to different needs
      of access patterns. Usually, each process is configured to read from a
      designated area within the netCDF variable.

  + **tst_var_iget/iput**
    * This series of tests is focused on the non-blocking mode of variable
      operations mentioned above. The program usually posts read(iget) or
      write(iput) requests to access a netCDF variable using explicit
      function-call style method and calls the wait function to commit them.

  + **tst_var_bput**
    * This series of tests is focused on the buffered non-blocking mode of
      variable operations mentioned above. The program usually attaches a write
      buffer to the netCDF file, posts read(iget) or write(iput) requests to
      access a netCDF variable and then calls the wait function to commit.

* **tst_default_format.py**
  + Test `set_default_format` function for creating a number of netCDF files
    with default format.

* **tst_rename.py**
  + Test `renameVariable/dim` functions of a `Dataset` instance for renaming
    previously defined variables and dimensions.

* **tst_version.py**
  + Test version string of PnetCDF-Python.

* **tst_wait.py**
  + Test non-blocking APIs and then use `wait/wait_all` method of `File` class
    to flush out the pending I/O requests.

* **tst_copy_attr.py**
  + Copying an attribute from one file to another in python can be done without
    `ncmpi_copy_att()`. For exampl, this can be done in two lines of python
    codes below:
    ```
    att = source_file.get_att("history")
    destition_file.put_att('history', att)
    ```

