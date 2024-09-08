#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
This example is the read counterpart of example put_var.py. It shows how to
use to `Variable` method get_var() read a 2D 4-byte integer array in parallel.
It also reads a global attribute and two attribute of variable named "var".
The data partitioning pattern is a column-wise partitioning across all
processes. Each process reads a subarray of size local_ny * local_nx.

To run:
     % mpiexec -n num_process python3 get_var.py [put_var_output_filename]

Input file is the output file produced by put_var.c. Here is the CDL dumped
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
"""

import sys, os, argparse
import numpy as np
from mpi4py import MPI
import pnetcdf

def pnetcdf_io(filename, file_format):

    # Open an existing file for reading
    f = pnetcdf.File(filename = filename,
                     mode = 'r',
                     comm = comm,
                     info = None)

    # Get global attribute named "history"
    str_att = f.get_att("history")
    if rank == 0 and verbose:
        print("global attribute \"history\" of text:", str_att)

    # Get dimension lengths for dimensions Y and X
    global_ny = len(f.dimensions['Y'])
    global_nx = len(f.dimensions['X'])

    if verbose and rank == 0:
        print("Y dimension size = ", global_ny)
        print("X dimension size = ", global_nx)

    # get the handler of variable named 'var', a 2D variable of integer type
    v = f.variables['var']

    # Get the variable's attribute named "str_att_name"
    str_att = v.str_att_name

    if rank == 0 and verbose:
        print("Read variable attribute \"str_att_name\" of type text =", str_att)

    # Equivalently, below uses function call
    str_att = v.get_att("str_att_name")

    if rank == 0 and verbose:
        print("Read variable attribute \"str_att_name\" of type text =", str_att)

    # Get the variable's attribute named "float_att_name"
    float_att = v.float_att_name

    # Equivalently, below uses function call
    float_att = v.get_att("float_att_name")

    # set access pattern for reading subarray
    local_ny = global_ny
    local_nx = global_nx // nprocs
    start = [0,  local_nx * rank]
    count = [local_ny, local_nx]
    end   = np.add(start, count)

    # allocate read buffer
    r_buf = np.empty(tuple(count), v.dtype)

    # Read a subarray in collective mode
    r_bufs = v[start[0]:end[0], start[1]:end[1]]

    # Equivalently, below uses function call
    v.get_var_all(r_buf, start = start, count = count)

    # close the file
    f.close()


def parse_help():
    help_flag = "-h" in sys.argv or "--help" in sys.argv
    if help_flag and rank == 0:
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


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nprocs = comm.Get_size()

    if parse_help():
        MPI.Finalize()
        sys.exit(1)

    # get command-line arguments
    args = None
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs="?", type=str, help="(Optional) output netCDF file name",\
                         default = "testfile.nc")
    parser.add_argument("-q", help="Quiet mode (reports when fail)", action="store_true")
    parser.add_argument("-k", help="File format: 1 for CDF-1, 2 for CDF-2, 5 for CDF-5")
    args = parser.parse_args()

    file_format = None
    length = 10

    verbose = False if args.q else True

    if args.k:
        kind_dict = {'1':None, '2':"NC_64BIT_OFFSET", '5':"NC_64BIT_DATA"}
        file_format = kind_dict[args.k]

    filename = args.dir

    if verbose and rank == 0:
        print("{}: reading file ".format(os.path.basename(__file__)), filename)

    try:
        pnetcdf_io(filename, file_format)
    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

