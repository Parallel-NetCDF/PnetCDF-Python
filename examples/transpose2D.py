####################################################################
# 
#  Copyright (C) 2014, Northwestern University 
#  See COPYRIGHT notice in top-level directory.
# 
####################################################################
"""
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
  This example shows how to use `Variable` method put_var() write a 2D integer array
  variable into a file. The variable in the file is a dimensional
  transposed array from the one stored in memory. In memory, a 2D array is
  partitioned among all processes in a block-block fashion in YX (i.e.
  row-major) order. The dimension structure of the transposed array is
  arrays are
        int YX_var(Y, X) ;
        int XY_var(X, Y) ;
 
    To run:
        % mpiexec -n num_process python3 transpose2D.py [filename] [-l len]
 
 where len decides the size of local array, which is len x (len+1).
 So, each variable is of size len*(len+1) * nprocs * sizeof(int)

 *    % mpiexec -n 4 python3 transpose2D.py testfile.nc
 *    % ncdump testfile.nc
 *    netcdf testfile {
 *    dimensions:
 *             Y = 4 ;
 *             X = 6 ;
 *    variables:
 *            int YX_var(Y, X) ;
 *            int XY_var(X, Y) ;
 *    data:
 *
 *     YX_var =
 *      0, 1, 2, 3, 4, 5,
 *      6, 7, 8, 9, 10, 11,
 *      12, 13, 14, 15, 16, 17,
 *      18, 19, 20, 21, 22, 23 ;
 *
 *     XY_var =
 *      0, 6, 12, 18,
 *      1, 7, 13, 19,
 *      2, 8, 14, 20,
 *      3, 9, 15, 21,
 *      4, 10, 16, 22,
 *      5, 11, 17, 23 ;
 *    }
 */
 
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

NDIMS = 2



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

    global verbose
    gsizes = np.zeros(NDIMS, dtype=np.int64)
    starts = np.zeros(NDIMS, dtype=np.int64)
    counts = np.zeros(NDIMS, dtype=np.int64)
    imap = np.zeros(NDIMS, dtype=np.int64)
    startsT = np.zeros(NDIMS, dtype=np.int64)
    countsT = np.zeros(NDIMS, dtype=np.int64)

    rank = comm.Get_rank()
    nprocs = comm.Get_size()


    psizes = MPI.Compute_dims(nprocs, NDIMS)

    if rank == 0:
        str = "psizes= "
        for i in range(NDIMS):
            str += "%d " % psizes[i]
        print(str)

    lower_dims = 1
    for i in range(NDIMS - 1, -1, -1):
        starts[i] = rank // lower_dims % psizes[i]
        lower_dims *= psizes[i]

    if verbose:
        str = "proc %d: dim rank= " % rank
        for i in range(NDIMS):
            str += "%d " % starts[i]
        print(str)

    bufsize = 1
    gsizes = np.zeros(NDIMS, dtype=np.int64)
    for i in range(NDIMS):
        gsizes[i] = (length + i) * psizes[i]
        starts[i] *= (length + i)
        counts[i] = (length + i)
        bufsize *= (length + i)

    buf = np.zeros(bufsize, dtype=np.int32)
    for i in range(counts[0]):
        for j in range(counts[1]):
            buf[i * counts[1] + j] = (starts[0] + i) * gsizes[1] + (starts[1] + j)


    # Create the file
    f = pncpy.File(filename=filename, mode = 'w', format = file_format, comm=comm, info=None)

    # Define dimensions
    dim_y = f.def_dim("Y", gsizes[0])
    dim_x = f.def_dim("X", gsizes[1])

    # Define variable with no transposed file layout: ZYX
    var_yx = f.def_var("YX_var", pncpy.NC_INT, (dim_y, dim_x))
    var_xy = f.def_var("XY_var", pncpy.NC_INT, (dim_x, dim_y))

     # Exit the define mode
    f.enddef()
    # Write the whole variable in file: ZYX
    var_yx.put_var_all(buf, start=starts, count=counts)
    # Transpose YX -> XY */
    imap[0] = 1
    imap[1] = counts[1]
    startsT[0] = starts[1]
    startsT[1] = starts[0]
    countsT[0] = counts[1]
    countsT[1] = counts[0]
    var_xy.put_var_all(buf, start = startsT, count = countsT, imap = imap)
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
    parser.add_argument("-l", help="size of each dimension of the local array")
    args = parser.parse_args()
    file_format = None
    length = 2
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
    pnetcdf_io(comm, filename, file_format, length)
    pnetcdf_check_mem_usage(comm)
    MPI.Finalize()

if __name__ == "__main__":
    main()
