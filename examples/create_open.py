####################################################################
# 
#  Copyright (C) 2014, Northwestern University 
#  See COPYRIGHT notice in top-level directory.
# 
####################################################################
"""
 This example shows how to use `File` class constructor to create a netCDF file and to 
 open the file for read only.

 Example commands for MPI run and outputs from running ncmpidump on the
 netCDF file produced by this example program:
    % mpiexec -n 4 python3  create_open.py /tmp/test1.nc
    % ncmpidump /tmp/test1.nc
        netcdf test1 {
        // file format: CDF-1
        }

"""

import sys
import os
from mpi4py import MPI
import pncpy
from pncpy import inq_malloc_max_size, inq_malloc_size
import argparse

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
    global verbose
    malloc_size, sum_size = 0, 0
    # print info about PnetCDF internal malloc usage
    malloc_size = inq_malloc_max_size()
    sum_size = comm.reduce(malloc_size, MPI.SUM, root=0)
    if rank == 0 and verbose:
        print("Maximum heap memory allocated by PnetCDF internally is {} bytes".format(sum_size))
    # check if there is any PnetCDF internal malloc residue
    malloc_size = inq_malloc_size()
    sum_size = comm.reduce(malloc_size, MPI.SUM, root=0)
    if rank == 0 and sum_size > 0:
        print("Heap memory allocated by PnetCDF internally has {} bytes yet to be freed".format(sum_size))


def main():
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
    f = pncpy.File(filename=filename, mode = 'w', comm=comm, info=None)
    # close the file
    f.close()
    # open the newly created file for read only
    f = pncpy.File(filename=filename, mode = 'r', comm=comm, info=None)
    # close the file
    f.close()
    pnetcdf_check_mem_usage(comm)

if __name__ == "__main__":
    main()
