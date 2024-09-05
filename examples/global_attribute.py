#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
This example shows how to use `File` method `put_att()` to write a global
attribute to a file.

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

import sys, os, argparse, time
import numpy as np
from mpi4py import MPI
import pnetcdf


def pnetcdf_io(filename, file_format):
    digit = np.int16([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    # Run pnetcdf i/o

    # Create the file
    f = pnetcdf.File(filename = filename,
                     mode = 'w',
                     format = file_format,
                     comm = comm,
                     info = None)

    if rank == 0:
        ltime = time.localtime()
        str_att = time.asctime(ltime)
    else:
        str_att = None

    # Make sure the time string is consistent among all processes
    str_att = comm.bcast(str_att, root=0)

    # write a global attribute
    f.history = str_att

    if rank == 0 and verbose:
        print(f'writing global attribute "history" of text {str_att}')

    # Equivalently, below uses function call
    f.put_att('history',str_att)

    # add another global attribute named "digits": an array of short type
    f.digits = digit
    if rank == 0 and verbose:
        print("writing global attribute \"digits\" of 10 short integers")

    # Equivalently, below uses function call
    f.put_att('digits', digit)

    # Close the file
    f.close()

    # Read the file
    f = pnetcdf.File(filename=filename, mode = 'r')

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
            "       [filename] (Optional) output netCDF file name\n"
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

    verbose = False if args.q else True

    file_format = None
    if args.k:
        kind_dict = {'1':None, '2':"NC_64BIT_OFFSET", '5':"NC_64BIT_DATA"}
        file_format = kind_dict[args.k]

    filename = args.dir

    if verbose and rank == 0:
        print("{}: example of put/get global attributes".format(os.path.basename(__file__)))

    try:
        pnetcdf_io(filename, file_format)
    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

