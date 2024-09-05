#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
This example shows how to use `Variable` method to write a 2D array user buffer
with ghost cells. The size of ghost cells is nghosts and the ghost cells cells
appear on both ends of each dimension. The contents of ghost cells are -8s and
non-ghost cells are the process rank IDs.

To run:
  % mpiexec -n num_process python3 ghost_cell.py [test_file_name]

Example commands for MPI run and outputs from running ncmpidump on the output
netCDF file produced by this example program:

  % mpiexec -n 4 python3 ghost_cell.py /tmp/test1.nc

  % ncmpidump /tmp/test1.nc
  netcdf testfile {
      // file format: CDF-5 (big variables)
      dimensions:
          Y = 8 ;
          X = 10 ;
      variables:
          int var(Y, X) ;
          data:

      var =
          0, 0, 0, 0, 0, 1, 1, 1, 1, 1,
          0, 0, 0, 0, 0, 1, 1, 1, 1, 1,
          0, 0, 0, 0, 0, 1, 1, 1, 1, 1,
          0, 0, 0, 0, 0, 1, 1, 1, 1, 1,
          2, 2, 2, 2, 2, 3, 3, 3, 3, 3,
          2, 2, 2, 2, 2, 3, 3, 3, 3, 3,
          2, 2, 2, 2, 2, 3, 3, 3, 3, 3,
          2, 2, 2, 2, 2, 3, 3, 3, 3, 3 ;
      }
  In this case, the contents of local buffers are shown below.

  rank 0:                                rank 1:
     -8, -8, -8, -8, -8, -8, -8, -8, -8     -8, -8, -8, -8, -8, -8, -8, -8, -8
     -8, -8, -8, -8, -8, -8, -8, -8, -8     -8, -8, -8, -8, -8, -8, -8, -8, -8
     -8, -8,  0,  0,  0,  0,  0, -8, -8     -8, -8,  1,  1,  1,  1,  1, -8, -8
     -8, -8,  0,  0,  0,  0,  0, -8, -8     -8, -8,  1,  1,  1,  1,  1, -8, -8
     -8, -8,  0,  0,  0,  0,  0, -8, -8     -8, -8,  1,  1,  1,  1,  1, -8, -8
     -8, -8,  0,  0,  0,  0,  0, -8, -8     -8, -8,  1,  1,  1,  1,  1, -8, -8
     -8, -8, -8, -8, -8, -8, -8, -8, -8     -8, -8, -8, -8, -8, -8, -8, -8, -8
     -8, -8, -8, -8, -8, -8, -8, -8, -8     -8, -8, -8, -8, -8, -8, -8, -8, -8

  rank 2:                                rank 3:
     -8, -8, -8, -8, -8, -8, -8, -8, -8     -8, -8, -8, -8, -8, -8, -8, -8, -8
     -8, -8, -8, -8, -8, -8, -8, -8, -8     -8, -8, -8, -8, -8, -8, -8, -8, -8
     -8, -8,  2,  2,  2,  2,  2, -8, -8     -8, -8,  3,  3,  3,  3,  3, -8, -8
     -8, -8,  2,  2,  2,  2,  2, -8, -8     -8, -8,  3,  3,  3,  3,  3, -8, -8
     -8, -8,  2,  2,  2,  2,  2, -8, -8     -8, -8,  3,  3,  3,  3,  3, -8, -8
     -8, -8,  2,  2,  2,  2,  2, -8, -8     -8, -8,  3,  3,  3,  3,  3, -8, -8
     -8, -8, -8, -8, -8, -8, -8, -8, -8     -8, -8, -8, -8, -8, -8, -8, -8, -8
     -8, -8, -8, -8, -8, -8, -8, -8, -8     -8, -8, -8, -8, -8, -8, -8, -8, -8
"""

import sys, os, argparse
import numpy as np
from mpi4py import MPI
import pnetcdf


def pnetcdf_io(filename, file_format, length):

    count = [length, length + 1]
    psizes = MPI.Compute_dims(nprocs, 2)

    nghosts = 2

    if verbose and rank == 0:
        print("number of MPI processes =", nprocs)
        print("number of ghost cells =", nghosts)
        print("psizes=", psizes)

    # set global array sizes
    gsizes = np.zeros(2, dtype=np.int64)
    gsizes[0] = length * psizes[0]  # global array size
    gsizes[1] = (length + 1) * psizes[1]
    if verbose and rank == 0:
        print("global variable shape:", gsizes)

    # find its local rank IDs along each dimension
    local_rank = np.zeros(2, dtype=np.int32)
    local_rank[0] = rank // psizes[1]
    local_rank[1] = rank % psizes[1]
    if verbose:
        print("rank ",rank,": local_rank = ", local_rank)

    # set subarray access pattern
    count = np.array([length, length + 1], dtype=np.int64)
    start = np.array([local_rank[0] * count[0], local_rank[1] * count[1]],
                      dtype=np.int64)
    if verbose:
        print("rank ",rank,": start = ",start," count =", count)

    # Create the file
    f = pnetcdf.File(filename = filename,
                     mode = 'w',
                     format = file_format,
                     comm = comm,
                     info = None)

    # Define dimensions
    dim_y = f.def_dim("Y", gsizes[0])
    dim_x = f.def_dim("X",gsizes[1])

    # Define a 2D variable of integer type
    var = f.def_var("var", pnetcdf.NC_INT, (dim_y, dim_x))

    # Exit the define mode
    f.enddef()

    # allocate and initialize buffer with ghost cells on both ends of each dim
    buf = np.empty([2*nghosts+count[0], 2*nghosts+count[1]], dtype=np.int32)
    buf.fill(-8)

    # keep contents of ghost cells to -8, all others 'rank'
    buf[nghosts:nghosts+count[0], nghosts:nghosts+count[1]].fill(rank)

    # Write data to the variable
    end = np.add(start, count)
    var[start[0]:end[0], start[1]:end[1]] = buf[nghosts:nghosts+count[0], nghosts:nghosts+count[1]]

    # Equivalently, below uses function call
    var.put_var_all(buf[nghosts:nghosts+count[0], nghosts:nghosts+count[1]], start = start, count = count)

    # Close the file
    f.close()


def parse_help():
    help_flag = "-h" in sys.argv or "--help" in sys.argv
    if help_flag and rank == 0:
        help_text = (
            "Usage: {} [-h] | [-q] [file_name]\n"
            "       [-h] Print help\n"
            "       [-q] Quiet mode (reports when fail)\n"
            "       [-k format] file format: 1 for CDF-1, 2 for CDF-2, 5 for CDF-5\n"
            "       [-l len] size of each dimension of the local array\n"
            "       [filename] (Optional) output netCDF file name\n"
        ).format(sys.argv[0])
        print(help_text)
    return help_flag


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nprocs = comm.Get_size()

    if parse_help():
        MPI.Finalize()
        sys.exit(1)

    # get command-line arguments
    args = None
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs="?", type=str, help="(Optional) output netCDF file name",\
                         default = "testfile.nc")
    parser.add_argument("-q", help="Quiet mode (reports when fail)", action="store_true")
    parser.add_argument("-k", help="File format: 1 for CDF-1, 2 for CDF-2, 5 for CDF-5")
    parser.add_argument("-l", help="Size of each dimension of the local array\n")
    args = parser.parse_args()

    verbose = False if args.q else True

    file_format = None
    if args.k:
        kind_dict = {'1':None, '2':"NC_64BIT_OFFSET", '5':"NC_64BIT_DATA"}
        file_format = kind_dict[args.k]

    length = 4
    if args.l and int(args.l) > 0:
        length = int(args.l)

    filename = args.dir

    if verbose and rank == 0:
        print("{}: example of using buffers with ghost cells".format(os.path.basename(__file__)))

    try:
        pnetcdf_io(filename, file_format, length)
    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

