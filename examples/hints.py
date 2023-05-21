####################################################################
# 
#  Copyright (C) 2014, Northwestern University 
#  See COPYRIGHT notice in top-level directory.
# 
####################################################################
"""
 * This example sets two PnetCDF hints: nc_header_align_size and nc_var_align_size 
 and prints the hint values as well as the header size, header extent, and two variables' 
 starting file offsets.

 Example commands for MPI run and outputs from running ncmpidump on the
 netCDF file produced by this example program:
    % mpiexec -n 4 python3 hints.py tmp/test1.nc
    % ncmpidump tmp/test1.nc
    
    Example standard output:
    nc_header_align_size      set to = 1024
    nc_var_align_size         set to = 512
    nc_header_read_chunk_size set to = 256
    header size                      = 156
    header extent                    = 1024
    var_zy start file offset         = 1024
    var_yx start file offset         = 1536
 
"""

import sys
import os
from mpi4py import MPI
import pncpy
from pncpy import inq_malloc_max_size, inq_malloc_size
import argparse
import numpy as np

verbose = True
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def parse_help():
    help_flag = "-h" in sys.argv or "--help" in sys.argv
    if help_flag:
        if rank == 0:
            help_text = (
                "Usage: {} [-h] | [-q] [file_name]\n"
                "       [-h] Print help\n"
                "       [-q] Quiet mode (reports when fail)\n"
                "       [filename] (Optional) output netCDF file name\n"
            ).format(sys.argv[0])
            print(help_text)

    return help_flag

def pnetcdf_check_mem_usage(comm):
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

def print_hints(nc_file, nc_var1, nc_var2):
    value = np.zeros(MPI.MAX_INFO_VAL, dtype='c')
    header_size, header_extent, var_zy_start, var_yx_start = -1, -1, -1, -1
    h_align, v_align, h_chunk = -1, -1, -1
    info_used = MPI.INFO_NULL

    # Get header size, header extent, and variable offsets
    header_size = nc_file.inq_header_size()
    header_extent = nc_file.inq_header_extent()
    var_zy_start = nc_var1.inq_offset()
    var_yx_start = nc_var2.inq_offset()

    # Get hints from file info
    info_used = nc_file.inq_info()
    if info_used != MPI.INFO_NULL:
        value = info_used.Get("nc_header_align_size")
        if value is not None:
            h_align = int(value)
        value = info_used.Get("nc_var_align_size")
        if value is not None:
            v_align = int(value)
        value = info_used.Get("nc_header_read_chunk_size")
        if value is not None:
            h_chunk = int(value)
        info_used.Free()

    if h_align == -1:
        print("nc_header_align_size      is NOT set")
    else:
        print(f"nc_header_align_size      set to = {h_align:d}")

    if v_align == -1:
        print("nc_var_align_size         is NOT set")
    else:
        print(f"nc_var_align_size         set to = {v_align:d}")

    if h_chunk == -1:
        print("nc_header_read_chunk_size is NOT set")
    else:
        print(f"nc_header_read_chunk_size set to = {h_chunk:d}")

    print(f"header size                      = {header_size:d}")
    print(f"header extent                    = {header_extent:d}")
    print(f"var_zy start file offset         = {var_zy_start:d}")
    print(f"var_yx start file offset         = {var_yx_start:d}")

def main():
    NY = 5
    NX = 5
    NZ = 5
    nprocs = size
    
    global verbose
    if parse_help():
        MPI.Finalize()
        return 1
    # get command-line arguments
    args = None
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs="?", type=str, help="(Optional) output netCDF file name",\
                         default = "testfile.nc")
    parser.add_argument("-q", help="Quiet mode (reports when fail)", action="store_true")
    args = parser.parse_args()
    if args.q:
        verbose = False
    filename = args.dir
    if verbose and rank == 0:
        print("{}: example of file create and open".format(__file__))
    # create MPI info 
    info1 = MPI.Info.Create()
    info1.Set("nc_header_align_size", "1024")
    info1.Set("nc_var_align_size", "512")
    info1.Set("nc_header_read_chunk_size", "256")
    # create a new file for writing
    f = pncpy.File(filename=filename, mode = 'w', file_format = "64BIT_DATA", comm=comm, info=info1)
    # define the dimensions
    dim_z = f.def_dim('Z', NZ*nprocs)
    dim_y = f.def_dim('Y', NY*nprocs)
    dim_x = f.def_dim('x', NX*nprocs)
    # define a variable of size (NZ * nprocs) * (NY * nprocs) 
    var_zy = f.def_var("var_zy", pncpy.NC_INT, (dim_z, dim_y))
    var_yx =  f.def_var("var_yx", pncpy.NC_FLOAT, (dim_y, dim_x))

    # exit the define mode
    f.enddef()
    # var_zy is partitioned along Z dimension
    buf_zy = np.empty(shape = (NZ * NY * nprocs, ), dtype = "i4")
    for i in range(NZ*NY*nprocs):
        buf_zy[i] = i
    start = [NZ * rank, 0]
    count =[NZ, NY * nprocs]
    var_zy.put_var_all(buf_zy, start = start, count = count)
    # var_yx is partitioned along X dimension
    buf_yx = np.empty(shape = (NX * NY * nprocs, ), dtype = "f4")
    for i in range(NX*NY*nprocs):
        buf_yx[i] = i
    start = [0, NX*rank]
    count =[NY * nprocs, NX]
    var_yx.put_var_all(buf_yx, start = start, count = count)

    if verbose and rank == 0:
        print_hints(f, var_zy, var_yx)
    info1.Free()
    f.close()

    # check PnetCDF library internal memory usage
    pnetcdf_check_mem_usage(comm)
    MPI.Finalize()

if __name__ == "__main__":
    main()
