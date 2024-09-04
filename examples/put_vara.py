#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
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
"""

import sys, os, argparse
import numpy as np
from mpi4py import MPI
import pnetcdf


def parse_help():
    help_flag = "-h" in sys.argv or "--help" in sys.argv
    if help_flag and rank == 0:
        help_text = (
            "Usage: {} [-h] | [-q] [file_name]\n"
            "       [-h] Print help\n"
            "       [-q] Quiet mode (reports when fail)\n"
            "       [-k format] file format: 1 for CDF-1, 2 for CDF-2, 5 for CDF-5\n"
            "       [filename] (Optional) output netCDF file name\n"
        ).format(sys.argv[0])
        print(help_text)
    return help_flag


def pnetcdf_io(filename, file_format):
    NY = 10
    NX = 4
    global_ny = NY
    global_nx = NX * nprocs
    start = [0, NX * rank]
    count = [NY, NX]

    if verbose and rank == 0:
        print("Y dimension size = ", NY)
        print("X dimension size = ", NX)

    # Create the file
    f = pnetcdf.File(filename = filename,
                     mode = 'w',
                     format = file_format,
                     comm = comm,
                     info = None)

    # Add a global attribute: a time stamp at rank 0
    if rank == 0:
        str_att = "Sun May 14 15:47:48 2023"
    else:
        str_att = None

    # Make sure the time string is consistent among all processes
    str_att = comm.bcast(str_att, root=0)

    # write a global attribute
    f.put_att('history',str_att)

    # Define dimensions
    dim_y = f.def_dim("Y", global_ny)
    dim_x = f.def_dim("X",global_nx)

    # Define a 2D variable of integer type
    var = f.def_var("var", pnetcdf.NC_INT, (dim_y, dim_x))

    # Add attributes to the variable
    str_att = "example attribute of type text."
    var.put_att("str_att_name", str_att)

    float_att = np.arange(8, dtype = 'f4')
    var.put_att("float_att_name", float_att)

    short_att = np.int16(1000)
    var.put_att("short_att_name", short_att)

    # Exit the define mode
    f.enddef()

    # initialize write buffer
    buf = np.zeros(shape = (NY, NX), dtype = "i4") + rank

    # Write data to the variable
    # var.put_var_all(buf, start = starts, count = counts)
    var[0:NY, NX*rank:NX*rank+NX] = buf

    # Close the file
    f.close()


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

    verbose = False if args.q else True

    file_format = None
    if args.k:
        kind_dict = {'1':None, '2':"NC_64BIT_OFFSET", '5':"NC_64BIT_DATA"}
        file_format = kind_dict[args.k]

    filename = args.dir

    if verbose and rank == 0:
        print("{}: example of writing subarrays".format(os.path.basename(__file__)))

    try:
        pnetcdf_io(filename, file_format)
    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

