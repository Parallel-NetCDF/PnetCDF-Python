####################################################################
# 
#  Copyright (C) 2014, Northwestern University 
#  See COPYRIGHT notice in top-level directory.
# 
####################################################################
"""
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
  This example shows how to use `Variable` method put_var() and iput_var() to write a 2D 4-byte
  integer array in parallel (one is of 4-byte
  integer byte and the other float type) in parallel. It first defines 2 netCDF
  variables of sizes
     var_zy: NZ*nprocs x NY
     var_yx: NY x NX*nprocs
 
  The data partitioning patterns on the 2 variables are row-wise and
  column-wise, respectively. Each process writes a subarray of size
  NZ x NY and NY x NX to var_zy and var_yx, respectively.
  Both local buffers have a ghost cell of length 3 surrounded along each
  dimension.
    To run:
        % mpiexec -n num_process python3 flexible_api.py [test_file_name]
 
  Example commands for MPI run and outputs from running ncmpidump on the
  output netCDF file produced by this example program:
 
     % mpiexec -n 4 python3 flexible_api.py /tmp/test1.nc
 
     % ncmpidump /tmp/test1.nc
     netcdf testfile {
     // file format: CDF-5 (big variables)
     dimensions:
             Z = 20 ;
             Y = 5 ;
             X = 20 ;
     variables:
             int var_zy(Z, Y) ;
             float var_yx(Y, X) ;
     data:
 
      var_zy =
       0, 0, 0, 0, 0,
       0, 0, 0, 0, 0,
       0, 0, 0, 0, 0,
       0, 0, 0, 0, 0,
       0, 0, 0, 0, 0,
       1, 1, 1, 1, 1,
       1, 1, 1, 1, 1,
       1, 1, 1, 1, 1,
       1, 1, 1, 1, 1,
       1, 1, 1, 1, 1,
       2, 2, 2, 2, 2,
       2, 2, 2, 2, 2,
       2, 2, 2, 2, 2,
       2, 2, 2, 2, 2,
       2, 2, 2, 2, 2,
       3, 3, 3, 3, 3,
       3, 3, 3, 3, 3,
       3, 3, 3, 3, 3,
       3, 3, 3, 3, 3,
       3, 3, 3, 3, 3 ;
 
      var_yx =
       0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3,
       0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3,
       0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3,
       0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3,
       0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3 ;
     }
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
from pncpy import strerror, strerrno

verbose = True

NY = 5
NX = 5
NZ = 5


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

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    nprocs = size
    ghost_len = 3
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
    args = parser.parse_args()
    file_format = None
    length = 10
    if args.q:
        verbose = False
    if args.k:
        kind_dict = {'1':None, '2':"64BIT_OFFSET", '5':"64BIT_DATA"}
        file_format = kind_dict[args.k]
    filename = args.dir
    if verbose and rank == 0:
        print("{}: example of file create and open".format(__file__))

    # Create the file
    f = pncpy.File(filename=filename, mode = 'w', format = file_format, comm=comm, info=None)
    # Define dimensions

    dim_z = f.def_dim("Z", NZ*nprocs)
    dim_y = f.def_dim("Y", NY)
    dim_x = f.def_dim("X", NX*nprocs)
    # define a variable of size (NZ * nprocs) * NY
    var_zy = f.def_var("var_zy", pncpy.NC_INT, (dim_z, dim_y))
    # define a variable of size NY * (NX * nprocs)
    var_yx = f.def_var("var_yx", pncpy.NC_FLOAT, (dim_y, dim_x))
    f.enddef()

    array_of_sizes = np.array([NZ + 2 * ghost_len, NY + 2 * ghost_len])
    array_of_subsizes = np.array([NZ, NY])
    array_of_starts = np.array([ghost_len, ghost_len])
    subarray = MPI.INT.Create_subarray(array_of_sizes, array_of_subsizes, array_of_starts, order=MPI.ORDER_C)
    subarray.Commit()

    buffer_len = (NZ + 2 * ghost_len) * (NY + 2 * ghost_len)
    buf_zy = np.full(buffer_len, rank, dtype=np.int32)

    starts = np.array([NZ * rank, 0])
    counts = np.array([NZ, NY])
    # calling a blocking flexible API using put_var_all()
    var_zy.put_var_all(buf_zy, start = starts, count = counts, bufcount = 1, buftype = subarray)


    for i in range(buffer_len):
        if buf_zy[i] != rank:
            print(f"Error at line {sys._getframe().f_lineno} in {__file__}: put buffer[{i}] is altered")

    buf_zy.fill(-1)
    var_zy.get_var_all(buf_zy, start = starts, count = counts, bufcount = 1, buftype = subarray)
    # print(buf_zy.reshape(array_of_sizes))
    
    # check contents of the get buffer
    for i in range(array_of_sizes[0]):
        for j in range(array_of_sizes[1]):
            index = i*array_of_sizes[1] + j
            if i < ghost_len or ghost_len + array_of_subsizes[0] <= i or j < ghost_len or ghost_len + array_of_subsizes[1] <= j:
                if buf_zy[index] != -1:
                    print(f"Unexpected get buffer[{i}][{j}]={buf_zy[index]}")
            else:
                if buf_zy[index] != rank:
                    print(f"Unexpected get buffer[{i}][{j}]={buf_zy[index]}")

    subarray.Free()
    # var_yx is partitioned along X dimension
    array_of_sizes = np.array([NY + 2 * ghost_len, NX + 2 * ghost_len])
    array_of_subsizes = np.array([NY, NX])
    array_of_starts = np.array([ghost_len, ghost_len])
    subarray = MPI.DOUBLE.Create_subarray(array_of_sizes, array_of_subsizes, array_of_starts, order=MPI.ORDER_C)
    subarray.Commit()

    buffer_len = (NY + 2 * ghost_len) * (NX + 2 * ghost_len)
    buf_yx = np.full(buffer_len, rank, dtype=np.float64)
    starts = np.array([0, NX * rank])
    counts = np.array([NY, NX])

    # calling a blocking flexible API using put_var_all()
    req_id = var_yx.iput_var(buf_yx, start = starts, count = counts, bufcount = 1, buftype=subarray)
    status = [None]
    f.wait_all(1, [req_id], status = status)
    # check request error msg for each unsuccessful requests
    if strerrno(status[0]) != "NC_NOERR":
        print(f"Error on request {i}:",  strerror(status[0]))

    buf_yx.fill(-1)
    req_id = var_yx.iget_var(buf_yx, start = starts, count = counts, bufcount = 1, buftype=subarray)
    f.wait_all(1, [req_id], status = status)
    # check request error msg for each unsuccessful requests
    if strerrno(status[0]) != "NC_NOERR":
        print(f"Error on request {i}:",  strerror(status[0]))

    # check the contents of iget buffer
    for i in range(array_of_sizes[0]):
        for j in range(array_of_sizes[1]):
            index = i * array_of_sizes[1] + j
            if i < ghost_len or ghost_len + array_of_subsizes[0] <= i or j < ghost_len or ghost_len + array_of_subsizes[1] <= j:
                if buf_yx[index] != -1:
                    print(f"Unexpected get buffer[{i}][{j}]={buf_yx[index]}")
            else:
                if buf_yx[index] != rank:
                    print(f"Unexpected get buffer[{i}][{j}]={buf_yx[index]}")
    subarray.Free()
    f.close()
    pnetcdf_check_mem_usage(comm)
    MPI.Finalize()

if __name__ == "__main__":
    main()
