####################################################################
# 
#  Copyright (C) 2014, Northwestern University 
#  See COPYRIGHT notice in top-level directory.
# 
####################################################################
"""
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
  This example shows how to use `File` API to write a 2D 4-byte
  integer array in parallel. It first defines a netCDF variable of size
  global_ny * global_nx where
     global_ny == NY and
     global_nx == (NX * number of MPI processes).
  The data partitioning pattern is a column-wise partitioning across all
  processes. Each process writes a subarray of size ny * nx.
 
    To run:
        % mpiexec -n num_process python3 global_attribute.py [test_file_name]
 
  Example commands for MPI run and outputs from running ncmpidump on the
  netCDF file produced by this example program:
    % mpiexec -n 4 python3 global_attribute.py ./tmp/test2.nc
     % ncmpidump ./tmp/test2.nc
     netcdf testfile {
     // file format: CDF-1

     // global attributes:
                     :history = "Sun May 21 00:02:46 2023" ;
         "" ;
                     :digits = 0s, 1s, 2s, 3s, 4s, 5s, 6s, 7s, 8s, 9s ;
     }
 
"""

import sys
import os
from mpi4py import MPI
import pncpy
from pncpy import inq_malloc_max_size, inq_malloc_size
import argparse
import numpy as np
import inspect
import time


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
    global verbose
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    digit = np.int16([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    nprocs = size

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
    if args.q:
        verbose = False
    if args.k:
        kind_dict = {'1':None, '2':"64BIT_OFFSET", '5':"64BIT_DATA"}
        file_format = kind_dict[args.k]
    filename = args.dir
    if verbose and rank == 0:
        print("{}: example of file create and open".format(__file__))
    # Run pnetcdf i/o

    # Create the file
    f = pncpy.File(filename=filename, mode = 'w', format = file_format, comm=comm, info=None)
    
    if rank == 0:
        ltime = time.localtime()
        str_att = time.asctime(ltime)
    else:
        str_att = None

    # Make sure the time string is consistent among all processes
    str_att = comm.bcast(str_att, root=0)
    f.put_att('history',str_att)
    if rank == 0 and verbose:
        print(f'writing global attribute "history" of text {str_att}')
    # add another global attribute named "digits": an array of short type
    f.put_att('digits', digit)
    if rank == 0 and verbose:
        print("writing global attribute \"digits\" of 10 short integers")
    # Close the file
    f.close()
    # Read the file
    f = pncpy.File(filename=filename, mode = 'r')
    # get the number of attributes
    ngatts = len(f.ncattrs())
    if ngatts != 2:
        print(f"Error at line {sys._getframe().f_lineno} in {__file__}: expected number of global attributes is 2, but got {ngatts}")
    # Find the name of the first global attribute
    att_name = f.ncattrs()[0]
    if att_name != "history":
        print(f"Error: Expected attribute name 'history', but got {att_name}")
    # Read attribute value
    str_att = f.get_att(att_name)
    # Find the name of the second global attribute
    att_name = f.ncattrs()[1]
    if att_name != "digits":
        print(f"Error: Expected attribute name 'digits', but got {att_name}")
    # Read attribute value
    short_att = f.get_att(att_name)
    f.close()
    pnetcdf_check_mem_usage(comm)
    MPI.Finalize()

if __name__ == "__main__":
    main()
