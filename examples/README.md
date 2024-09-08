# PnetCDF-python examples

This directory contains example python programs that make use of PnetCDF to
perform file I/O in parallel. Detailed description of each program and run
instructions can be found at the beginning of each file.

---
### Running individual example programs

* Use command `mpiexec` to run individual programs. For example, command
  line below run `collective_write.py` on 4 MPI processes.
  ```sh
  mpiexec -n 4 python collective_write.py [output_dir]
  ```
* The optional argument `output_dir` enables the testing program to save the
  generated output files in the specified directory. Default is the current
  directory.

---
### Overview of Test Programs

* [MNIST](./MNIST)
  + A directory contains an example of
    [Pytorch MNIST](https://github.com/pytorch/examples/tree/main/mnist),
    using Pytorch module `DistributedDataParallel` for parallel training and
    `PnetCDF-Python` for reading data from a NetCDF files.

* [Pytorch_DDP](./Pytorch_DDP)
  + A directory contains examples that make use of Pytorch Distributed Data
    Parallel module to run python programs in parallel.

* [nonblocking](./nonblocking)
  + A directory contains examples that make use of nonblocking I/O APIs.
    * [nonblocking_write.py](./nonblocking/nonblocking_write.py) --
      Similar to `collective_write.py`, this example uses nonblocking APIs
      instead. It creates a netcdf file in CDF-5 format and writes a number of
      3D integer non-record variables.
    * [nonblocking_read.py](./nonblocking/nonblocking_read.py) --
      A read counterpart of `nonblocking_write.py`. It reads the output file
      generated from `nonblocking_write.py`.
    * [nonblocking_write_def.py](./nonblocking/nonblocking_write_def.py) --
      This example is the same as `nonblocking_write.py` expect all nonblocking
      write requests (calls to `iput` and `bput`) are posted in define mode. It
      creates a netcdf file in CDF-5 format and writes a number of 3D integer
      non-record variables.

* [create_open.py](./create_open.py)
  + This example shows how to use `File` class constructor to create a NetCDF
    file and to open the file for read only.

* [put_var.py](./put_var.py)
  + This example shows how to use `Variable` method put_var() to write a 2D
    integer array in parallel. The data partitioning pattern is a column-wise
    partitioning across all processes.

* [get_var.py](./get_var.py)
  + This example is the read counterpart of [put_var.py](./put_var.py), which
    shows how to use to `Variable` method get_var() read a 2D 4-byte integer
    array in parallel.

* [collective_write.py](./collective_write.py)
  + This example writes multiple 3D subarrays to non-record variables of int
    type using collective I/O mode.

* [ghost_cell.py](./ghost_cell.py)
  + This example shows how to use `Variable` method to write a 2D array user
    buffer with ghost cells.

* [fill_mode.py](./fill_mode.py)
  + This example shows how to use `Variable` class methods and `File` class
    methods to set the fill mode of variables and fill values.
    * `set_fill()` to enable fill mode of the file
    * `def_fill()` to enable fill mode and define the variable's fill value
    * `inq_var_fill()` to inquire the variable's fill mode information
    * `put_var_all()` to write two 2D 4-byte integer array in parallel.

* [global_attribute.py](./global_attribute.py)
  + This example shows how to use `File` method `put_att()` to write a global
    attribute to a file.

* [flexible_api.py](./flexible_api.py)
  + This example shows how to use `Variable` flexible API methods put_var() and
    iput_var() to write a 2D 4-byte integer array in parallel.

* [hints.py](./hints.py)
  + This example sets two PnetCDF hints: `nc_header_align_size` and
    `nc_var_align_size` and prints the hint values as well as the header size,
    header extent, and two variables' starting file offsets.

* [get_info.py](./get_info.py)
  + This example prints all MPI-IO hints used.

* [transpose2D.py](./transpose2D.py)
  + This example shows how to use `Variable` method `put_var()` to write a 2D
    integer array variable into a file. The variable in the file is a
    dimensional transposed array from the one stored in memory.

* [transpose.py](./transpose.py)
  + This example shows how to use `Variable` method `put_var()` to write six 3D
    integer array variables into a file. Each variable in the file is a
    dimensional transposed array from the one stored in memory. In memory, a 3D
    array is partitioned among all processes in a block-block-block fashion and
    in ZYX (i.e.  C) order. The dimension structures of the transposed six
    arrays are
    * int ZYX_var(Z, Y, X) ;     ZYX -> ZYX
    * int ZXY_var(Z, X, Y) ;     ZYX -> ZXY
    * int YZX_var(Y, Z, X) ;     ZYX -> YZX
    * int YXZ_var(Y, X, Z) ;     ZYX -> YXZ
    * int XZY_var(X, Z, Y) ;     ZYX -> XZY
    * int XYZ_var(X, Y, Z) ;     ZYX -> XYZ

* [put_varn_int.py](./put_varn_int.py)
  + This example shows how to use a single call of `Variable` method
    `put_varn()` to write a sequence of subarray requests to a variable with
    arbitrary array indices and lengths.

