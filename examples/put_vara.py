####################################################################
# 
#  Copyright (C) 2014, Northwestern University 
#  See COPYRIGHT notice in top-level directory.
# 
####################################################################
"""
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
  This example shows how to use `Variable` method put_var() to write a 2D 4-byte
  integer array in parallel. It first defines a netCDF variable of size
  global_ny * global_nx where
     global_ny == NY and
     global_nx == (NX * number of MPI processes).
  The data partitioning pattern is a column-wise partitioning across all
  processes. Each process writes a subarray of size ny * nx.
 
    To run:
        % mpiexec -n num_process python3 put_vara.py [test_file_name]
 
  Example commands for MPI run and outputs from running ncmpidump on the
  output netCDF file produced by this example program:
 
     % mpiexec -n num_process python3 put_vara.py /tmp/test1.nc
 
     % ncmpidump /tmp/test1.nc
    netcdf test1 {
    // file format: CDF-1
    dimensions:
            Y = 10 ;
            X = 16 ;
    variables:
            int var(Y, X) ;
                    var:str_att_name = "example attribute of type text." ;
                    var:float_att_name = 0.f, 1.f, 2.f, 3.f, 4.f, 5.f, 6.f, 7.f ;
                    var:short_att_name = 1000s ;

    // global attributes:
                    :history = "Sun May 14 15:47:48 2023" ;
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

NY = 10
NX = 4


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

def pnetcdf_io(comm, filename, file_format):
    rank = comm.Get_rank()
    nprocs = comm.Get_size()

    buf = np.zeros(shape = (NY, NX), dtype = "i4") + rank
    str_att = ""
    float_att = np.arange(8, dtype = 'f4')
    short_att = np.int16(1000)
    global_ny = NY
    global_nx = NX * nprocs
    starts = [0, NX * rank]
    counts = [NY, NX]


    # Create the file
    f = pncpy.File(filename=filename, mode = 'w', format = file_format, comm=comm, info=None)
    # Add a global attribute: a time stamp at rank 0
    if rank == 0:
        str_att = "Sun May 14 15:47:48 2023"
    else:
        str_att = None
    # Make sure the time string is consistent among all processes
    str_att = comm.bcast(str_att, root=0)
    f.put_att('history',str_att)
    # Define dimensions
    dim_y = f.def_dim("Y", global_ny)
    dim_x = f.def_dim("X",global_nx)
    # Define a 2D variable of integer type
    var = f.def_var("var", pncpy.NC_INT, (dim_y, dim_x))
    # Add attributes to the variable
    str_att = "example attribute of type text."
    var.put_att("str_att_name", str_att)
    var.put_att("float_att_name", float_att)
    var.put_att("short_att_name", short_att)

     # Exit the define mode
    f.enddef()
    # Write data to the variable
    var.put_var_all(buf, start = starts, count = counts)
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
