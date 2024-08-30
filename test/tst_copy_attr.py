#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
This program tests how to copy an attribute from a file to another. Note that
there is no ncmpi_copy_att() function in PnetCDF-Python. This is because
copying a python object is much simpler than in C. In C, without
ncmpi_copy_att(), one have to do the followings.
1. find the size and type of the attribute from the source file
2. malloc space, read from the source file
3. write to the destination file
4. free the buffer

In python, this can be done in two lines of codes:
   att = source_file.get_att("history")
   destition_file.put_att('history', att)

To run:
  % mpiexec -n num_process python3 tst_copy_attr.py [test_file_name]

  Example commands for MPI run and outputs from running ncmpidump on the
  output netCDF file produced by this example program:

  % mpiexec -n num_process python3 tst_copy_attr.py testfile.nc

  % ncmpidump testfile.nc
    netcdf testfile {
    // file format: CDF-1
    variables:
        int var0 ;
                var0:history = "today" ;

    // global attributes:
                :history = "today" ;
    data:

     var0 = 0 ;
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
            "Usage: {} [-h] | [-v] [file_name]\n"
            "       [-h] Print help\n"
            "       [-v] Verbose mode\n"
            "       [-k format] file format: 1 for CDF-1, 2 for CDF-2, 5 for CDF-5\n"
            "       [filename] (Optional) output netCDF file name\n"
        ).format(sys.argv[0])
        print(help_text)
    return help_flag


# Create two files and copy attributes from one file to another
def pnetcdf_io(filename, file_format):

    # Create the file
    f0 = pnetcdf.File(filename = filename, mode = 'w', format = file_format,
                      comm = comm, info = None)

    filename_dup = filename + "_dup.nc"
    f1 = pnetcdf.File(filename = filename_dup, mode = 'w', format = file_format,
                      comm = comm, info = None)

    # define a variable in each file
    v0 = f0.def_var('var0', 'i4', ())
    v1 = f1.def_var('var1', 'i4', ())

    # put a new global attribute in f0
    f0.put_att('history','today')

    # put a new attribute to variable v0 in f0
    v0.put_att('history','today')

    # retrieve the global attribute from f0
    att = f0.get_att("history")

    # copy it to f1
    f1.put_att('history', att)

    # retrieve v0's attribute from f0
    v_att = v0.get_att("history")

    # copy it to variable v1 in f1
    v1.put_att('history', v_att)

    # close files
    f0.close()
    f1.close()

    # Open file f1 and check the attribute contents
    f1 = pnetcdf.File(filename_dup, 'r', comm = comm)
    assert("today" == f1.get_att("history"))

    v1=f1.variables['var1']
    assert("today" == v1.get_att("history"))

    # close files
    f1.close()


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
    parser.add_argument("dir", nargs="?", type=str, help="(Optional) output directory name",\
                         default = ".")
    parser.add_argument("-v", help="Verbose mod ", action="store_true")
    parser.add_argument("-k", help="File format: 1 for CDF-1, 2 for CDF-2, 5 for CDF-5")
    args = parser.parse_args()

    verbose = True if args.v else False

    file_format = None
    if args.k:
        kind_dict = {'1':None, '2':"NC_64BIT_OFFSET", '5':"NC_64BIT_DATA"}
        file_format = kind_dict[args.k]

    filename = os.path.join(args.dir, "tst_copy_attr.nc")

    if verbose and rank == 0:
        print("{}: test copying attributes ".format(os.path.basename(__file__)))

    try:
        pnetcdf_io(filename, file_format)
    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

