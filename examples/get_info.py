####################################################################
# 
#  Copyright (C) 2014, Northwestern University 
#  See COPYRIGHT notice in top-level directory.
# 
####################################################################
"""

 Example commands for MPI run and outputs from running ncmpidump on the
 netCDF file produced by this example program:
    % mpiexec -n 4 python3 get_info.py tmp/test1.nc
    % ncmpidump tmp/test1.nc
        Example standard output:
    MPI File Info: nkeys = 18
    MPI File Info: [ 0] key =            cb_buffer_size, value = 16777216
    MPI File Info: [ 1] key =             romio_cb_read, value = automatic
    MPI File Info: [ 2] key =            romio_cb_write, value = automatic
    MPI File Info: [ 3] key =                  cb_nodes, value = 1
    MPI File Info: [ 4] key =         romio_no_indep_rw, value = false
    MPI File Info: [ 5] key =              romio_cb_pfr, value = disable
    MPI File Info: [ 6] key =         romio_cb_fr_types, value = aar
    MPI File Info: [ 7] key =     romio_cb_fr_alignment, value = 1
    MPI File Info: [ 8] key =     romio_cb_ds_threshold, value = 0
    MPI File Info: [ 9] key =         romio_cb_alltoall, value = automatic
    MPI File Info: [10] key =        ind_rd_buffer_size, value = 4194304
    MPI File Info: [11] key =        ind_wr_buffer_size, value = 524288
    MPI File Info: [12] key =             romio_ds_read, value = automatic
    MPI File Info: [13] key =            romio_ds_write, value = automatic
    MPI File Info: [14] key =            cb_config_list, value = *:1
    MPI File Info: [15] key =      nc_header_align_size, value = 512
    MPI File Info: [16] key =         nc_var_align_size, value = 512
    MPI File Info: [17] key = nc_header_read_chunk_size, value = 0
 
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

def print_info(info_used):
    nkeys = info_used.Get_nkeys()
    print("MPI File Info: nkeys =", nkeys)
    for i in range(nkeys):
        key = info_used.Get_nthkey(i)
        value = info_used.Get(key)
        print("MPI File Info: [{:2d}] key = {:25s}, value = {}".format(i, key, value))

    
def main():
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
    # create a new file using "w" mode
    f = pncpy.File(filename=filename, mode = 'w', file_format = "64BIT_DATA", comm=comm, info=None)
    # exit the define mode
    f.enddef()
    # get all the hints used
    info_used = f.inq_info()
    if verbose and rank == 0:
        print_info(info_used)
    info_used.Free()
    f.close()

    # check PnetCDF library internal memory usage
    pnetcdf_check_mem_usage(comm)
    MPI.Finalize()

if __name__ == "__main__":
    main()
