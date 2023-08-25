####################################################################
# 
#  Copyright (C) 2014, Northwestern University 
#  See COPYRIGHT notice in top-level directory.
# 
####################################################################
"""
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
  This example is the read counterpart of example put_vara.py. It shows how to
  use to `Variable` method get_var() read a 2D 4-byte integer array in parallel.
  It also reads a global attribute and two attribute of variable named "var".
  The data partitioning pattern is a column-wise partitioning across all
  processes. Each process reads a subarray of size local_ny * local_nx.
 
    To run:
        % mpiexec -n num_process python3 get_vara.py [put_vara_output_filename]
 
  Input file is the output file produced by put_vara.c. Here is the CDL dumped
  from running ncmpidump.
 
 
     % ncmpidump /tmp/test1.nc
     netcdf testfile {
     // file format: CDF-5 (big variables)
     dimensions:
             y = 10 ;
             x = 16 ;
     variables:
             int var(y, x) ;
                 var:str_att_name = "example attribute of type text." ;
                 var:float_att_name = 0.f, 1.f, 2.f, 3.f, 4.f, 5.f, 6.f, 7.f ;
                 var:short_att_name = 1000s ;
     // global attributes:
                 :history = "Mon Aug 13 21:27:48 2018" ;
        "" ;
     data:
 
      var =
          0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
          0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
          0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
          0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
          0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
          0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
          0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
          0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
          0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
          0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3 ;
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
                "       [filename] input netCDF file name\n"
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

def pnetcdf_io(comm, filename, file_format):
    rank = comm.Get_rank()
    nprocs = comm.Get_size()
    # Open an existing file for reading
    f = pncpy.File(filename=filename, mode = 'r', comm=comm, info=None)
    # Get global attribute named "history"
    str_att = f.get_att("history")
    if rank == 0 and verbose:
        print("global attribute \"history\" of text:", str_att)
    # Get dimension lengths for dimensions Y and X
    global_ny = len(f.dimensions['Y'])
    global_nx = len(f.dimensions['X'])
    # get the variable of a 2D variable of integer type
    v = f.variables['var']
    # Get the variable's attribute named "str_att_name"
    str_att = v.get_att("str_att_name")
    if rank == 0 and verbose:
        print("variable attribute \"str_att_name\" of type text =", str_att)
    # Get the length of the variable's attribute named "float_att_name"
    float_att =  v.get_att("float_att_name")
    # Prepare reading subarray
    local_ny = global_ny
    local_nx = global_nx // nprocs
    starts = [0,  local_nx * rank]
    counts = [local_ny, local_nx]
    # Read a subarray in collective mode
    buff = np.empty(tuple(counts), v.dtype)
    v.get_var_all(buff, start = starts, count = counts)
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
    parser.add_argument("dir", nargs="?", type=str, help="Input netCDF file name",\
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
    # Run pnetcdf i/o
    pnetcdf_io(comm, filename, file_format)
    pnetcdf_check_mem_usage(comm)
    MPI.Finalize()

if __name__ == "__main__":
    main()
