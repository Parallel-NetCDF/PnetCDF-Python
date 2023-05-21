####################################################################
# 
#  Copyright (C) 2014, Northwestern University 
#  See COPYRIGHT notice in top-level directory.
# 
####################################################################
"""
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
This example shows how to use `Variable` method to write a 2D array buffer with 
ghost cells to a variables. The size of ghost cells is nghosts and the ghost cells
cells appear on both ends of each dimension. The contents of ghost cells are
-8s and non-ghost cells are the process rank IDs.
 
    To run:
        % mpiexec -n num_process python3 ghost_cell.py [test_file_name]
 
  Example commands for MPI run and outputs from running ncmpidump on the
  output netCDF file produced by this example program:
 
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
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
"""

import sys
import os
from mpi4py import MPI
import pncpy
from pncpy import inq_malloc_max_size, inq_malloc_size
import argparse
import numpy as np
import inspect

verbose = True


def parse_help(comm):
    rank = comm.Get_rank()
    help_flag = "-h" in sys.argv or "--help" in sys.argv
    if help_flag:
        if rank == 0:
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

def pnetcdf_check_mem_usage(comm):
    rank = comm.Get_rank()
    malloc_size, sum_size = 0, 0
    # print info about PnetCDF internal malloc usage
    try:
        malloc_size = inq_malloc_max_size()
    except:
        return 
    else:
        sum_size = comm.reduce(malloc_size, MPI.SUM, root=0)
        if rank == 0 and verbose:
            print("Maximum heap memory allocated by PnetCDF internally is {} bytes".format(sum_size))
        # check if there is any PnetCDF internal malloc residue
        malloc_size = inq_malloc_size()
        sum_size = comm.reduce(malloc_size, MPI.SUM, root=0)
        if rank == 0 and sum_size > 0:
            print("Heap memory allocated by PnetCDF internally has {} bytes yet to be freed".format(sum_size))

def pnetcdf_io(comm, filename, file_format, length):
    rank = comm.Get_rank()
    nprocs = comm.Get_size()

    counts = [length, length + 1]
    psizes = MPI.Compute_dims(nprocs, 2)

    if verbose and rank == 0:
        print("psizes=", psizes[0], psizes[1])

    gsizes = np.zeros(2, dtype=np.int64)
    gsizes[0] = length * psizes[0]  # global array size
    gsizes[1] = (length + 1) * psizes[1]
    if verbose and rank == 0:
        print("global variable shape:", gsizes[0], gsizes[1])
    # find its local rank IDs along each dimension
    local_rank = np.zeros(2, dtype=np.int32)
    local_rank[0] = rank // psizes[1]
    local_rank[1] = rank % psizes[1]
    if verbose:
        print("rank {}: dim rank= {} {}".format(rank, local_rank[0], local_rank[1]))

    counts = np.array([length, length + 1], dtype=np.int64)
    starts = np.array([local_rank[0] * counts[0], local_rank[1] * counts[1]], dtype=np.int64)
    if verbose:
        print("starts= {} {} counts= {} {}".format(starts[0], starts[1], counts[0], counts[1]))
   # allocate and initialize buffer with ghost cells on both ends of each dim
    nghosts = 2
    bufsize = (counts[0] + 2 * nghosts) * (counts[1] + 2 * nghosts)
    buf = np.empty(bufsize, dtype=np.int32)
    for i in range(counts[0] + 2 * nghosts):
        for j in range(counts[1] + 2 * nghosts):
            if nghosts <= i < counts[0] + nghosts and nghosts <= j < counts[1] + nghosts:
                buf[i * (counts[1] + 2 * nghosts) + j] = rank
            else:
                buf[i * (counts[1] + 2 * nghosts) + j] = -8  # all ghost cells have value -8

    # Create the file
    f = pncpy.File(filename=filename, mode = 'w', format = file_format, comm=comm, info=None)

    # Define dimensions
    dim_y = f.def_dim("Y", gsizes[0])
    dim_x = f.def_dim("X",gsizes[1])
    # Define a 2D variable of integer type
    var = f.def_var("var", pncpy.NC_INT, (dim_y, dim_x))
     # Exit the define mode
    f.enddef()
    imap = np.zeros(2, dtype=np.int64)
    imap[1] = 1
    imap[0] = counts[1] + 2 * nghosts
    buf_ptr = buf[nghosts * (counts[1] + 2 * nghosts + 1):]
    # Write data to the variable
    var.put_var_all(buf_ptr, start = starts, count = counts, imap = imap)
    # Close the file
    f.close()

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    nprocs = size
    
    global verbose
    if parse_help(comm):
        MPI.Finalize()
        return 1
    # Get command-line arguments
    args = None
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs="?", type=str, help="(Optional) output netCDF file name",\
                         default = "testfile.nc")
    parser.add_argument("-q", help="Quiet mode (reports when fail)", action="store_true")
    parser.add_argument("-k", help="File format: 1 for CDF-1, 2 for CDF-2, 5 for CDF-5")
    parser.add_argument("-l", help="Size of each dimension of the local array\n")
    args = parser.parse_args()
    file_format = None
    length = 0
    if args.q:
        verbose = False
    if args.k:
        kind_dict = {'1':None, '2':"64BIT_OFFSET", '5':"64BIT_DATA"}
        file_format = kind_dict[args.k]
    if args.l:
        length = int(args.l)
    filename = args.dir
    if verbose and rank == 0:
        print("{}: example of file create and open".format(__file__))
    # Run pnetcdf i/o
    length = 4 if length <= 0 else length
    pnetcdf_io(comm, filename, file_format, length)
    pnetcdf_check_mem_usage(comm)
    MPI.Finalize()

if __name__ == "__main__":
    main()
