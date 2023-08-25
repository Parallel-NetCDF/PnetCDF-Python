####################################################################
# 
#  Copyright (C) 2014, Northwestern University 
#  See COPYRIGHT notice in top-level directory.
# 
####################################################################
"""
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
  This example shows how to use `Variable` method put_var() to write six 3D integer array
  variables into a file. Each variable in the file is a dimensional
  transposed array from the one stored in memory. In memory, a 3D array is
  partitioned among all processes in a block-block-block fashion and in
  ZYX (i.e. C) order. The dimension structures of the transposed six
  arrays are
        int ZYX_var(Z, Y, X) ;     ZYX -> ZYX
        int ZXY_var(Z, X, Y) ;     ZYX -> ZXY
        int YZX_var(Y, Z, X) ;     ZYX -> YZX
        int YXZ_var(Y, X, Z) ;     ZYX -> YXZ
        int XZY_var(X, Z, Y) ;     ZYX -> XZY
        int XYZ_var(X, Y, Z) ;     ZYX -> XYZ
 
    To run:
        % mpiexec -n num_process python3 transpose.py [filename] [-l len]
 
 where len decides the size of local array, which is len x (len+1) x (len+2).
 So, each variable is of size len*(len+1)*(len+2) * nprocs * sizeof(int)

 
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

NDIMS = 3



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




    gsizes = np.zeros(NDIMS, dtype=np.int64)
    starts = np.zeros(NDIMS, dtype=np.int64)
    counts = np.zeros(NDIMS, dtype=np.int64)
    imap = np.zeros(NDIMS, dtype=np.int64)
    startsT = np.zeros(NDIMS, dtype=np.int64)
    countsT = np.zeros(NDIMS, dtype=np.int64)

    rank = comm.Get_rank()
    nprocs = comm.Get_size()


    # calculate number of processes along each dimension
    psizes = MPI.Compute_dims(nprocs, NDIMS)
    if rank == 0:
        print("psizes =", psizes)

    # for each MPI rank, find its local rank IDs along each dimension in starts[]
    lower_dims = 1
    for i in range(NDIMS-1, -1, -1):
        starts[i] = rank // lower_dims % psizes[i]
        lower_dims *= psizes[i]
    if verbose:
        print("proc {}: dim rank = {}".format(rank, starts))
    bufsize = 1
    for i in range(NDIMS):
        gsizes[i] = (length + i) * psizes[i]  # global array size
        starts[i] *= (length + i)  # start indices
        counts[i] = (length + i)  # array elements
        bufsize *= (length + i)
    # allocate buffer and initialize with contiguous numbers
    buf = np.empty(bufsize, dtype=int)
    index = 0
    for k in range(counts[0]):
        for j in range(counts[1]):
            for i in range(counts[2]):
                buf[index] = (starts[0]+k)*gsizes[1]*gsizes[2] + (starts[1]+j)*gsizes[2] + (starts[2]+i)
                index += 1

    # Create the file
    f = pncpy.File(filename=filename, mode = 'w', format = file_format, comm=comm, info=None)

    # Define dimensions
    dim_z = f.def_dim("Z", gsizes[0])
    dim_y = f.def_dim("Y", gsizes[1])
    dim_x = f.def_dim("X", gsizes[2])

    # Define variable with no transposed file layout: ZYX
    var_zyx = f.def_var("ZYX_var", pncpy.NC_INT, (dim_z, dim_y, dim_x))

    # Define variable with transposed file layout: ZXY
    var_zxy = f.def_var("ZXY_var",  pncpy.NC_INT, (dim_z, dim_x, dim_y))

    # Define variable with transposed file layout: YZX
    var_yzx = f.def_var("YZX_var",  pncpy.NC_INT, (dim_y, dim_z, dim_x))

    # Define variable with transposed file layout: YXZ
    var_yxz = f.def_var("YXZ_var",  pncpy.NC_INT, (dim_y, dim_x, dim_z))

    # Define variable with transposed file layout: XZY
    var_xzy = f.def_var("XZY_var",  pncpy.NC_INT, (dim_x, dim_z, dim_y))

    # Define variable with transposed file layout: XYZ
    var_xyz = f.def_var("XYZ_var",  pncpy.NC_INT, (dim_x, dim_y, dim_z))

     # Exit the define mode
    f.enddef()
    # Write the whole variable in file: ZYX
    var_zyx.put_var_all(buf, start=starts, count=counts)
    # ZYX -> ZXY:
    imap[1] = 1; imap[2] = counts[2]; imap[0] = counts[1]*counts[2]
    startsT[0] = starts[0]; startsT[1] = starts[2]; startsT[2] = starts[1]
    countsT[0] = counts[0]; countsT[1] = counts[2]; countsT[2] = counts[1]
    var_zxy.put_var_all(buf, start = startsT, count = countsT, imap = imap)
    # ZYX -> ZXY:
    imap[1] = 1; imap[2] = counts[2]; imap[0] = counts[1]*counts[2]
    startsT[0] = starts[0]; startsT[1] = starts[2]; startsT[2] = starts[1]
    countsT[0] = counts[0]; countsT[1] = counts[2]; countsT[2] = counts[1]
    var_zxy.put_var_all(buf, start=startsT, count=countsT, imap=imap)

    # ZYX -> YZX:
    imap[2] = 1; imap[0] = counts[2]; imap[1] = counts[1]*counts[2]
    startsT[0] = starts[1]; startsT[1] = starts[0]; startsT[2] = starts[2]
    countsT[0] = counts[1]; countsT[1] = counts[0]; countsT[2] = counts[2]
    var_yzx.put_var_all(buf, start=startsT, count=countsT, imap=imap)

    # ZYX -> YXZ:
    imap[1] = 1; imap[0] = counts[2]; imap[2] = counts[1]*counts[2]
    startsT[0] = starts[1]; startsT[1] = starts[2]; startsT[2] = starts[0]
    countsT[0] = counts[1]; countsT[1] = counts[2]; countsT[2] = counts[0]
    var_yxz.put_var_all(buf, start=startsT, count=countsT, imap=imap)

    # ZYX -> XZY:
    imap[0] = 1; imap[2] = counts[2]; imap[1] = counts[1]*counts[2]
    startsT[0] = starts[2]; startsT[1] = starts[0]; startsT[2] = starts[1]
    countsT[0] = counts[2]; countsT[1] = counts[0]; countsT[2] = counts[1]
    var_xzy.put_var_all(buf, start=startsT, count=countsT, imap=imap)

    # ZYX -> XYZ:
    imap[0] = 1; imap[1] = counts[2]; imap[2] = counts[1]*counts[2]
    startsT[0] = starts[2]; startsT[1] = starts[1]; startsT[2] = starts[0]
    countsT[0] = counts[2]; countsT[1] = counts[1]; countsT[2] = counts[0]
    var_xyz.put_var_all(buf, start=startsT, count=countsT, imap=imap)

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
    length = 10
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
