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

  % mpiexec -n 4 python3 global_attribute.py testfile.nc
  % ncmpidump testfile.nc
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


def write_attr(filename, file_format):

    # Create a new file
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

    # write a global attribute of string data type
    f.history = str_att

    # Equivalently, this can also be done by using a function call
    f.put_att('history',str_att)

    if rank == 0 and verbose:
        print(f'writing global attribute "history" of text {str_att}')

    # add another global attribute named "digits": an array of type int16
    digits = np.int16([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    f.digits = digits

    # Equivalently, this can also be done by using a function call
    f.put_att('digits', digits)

    if rank == 0 and verbose:
        print("writing global attribute \"digits\" of 10 short integers")

    # Close the file
    f.close()


def read_attr(filename):

    # Open the file for read
    f = pnetcdf.File(filename = filename, mode = 'r')

    # obtain the name list of all global attributes
    gatt_names = f.ncattrs()

    # the number of global attributes
    ngatts = len(gatt_names)
    if ngatts != 2:
        print(f"Error at line {sys._getframe().f_lineno} in {__file__}: expected number of global attributes is 2, but got {ngatts}")
    elif verbose and rank == 0:
        print("Number of global attributes = ", ngatts)

    # Find the name of the first global attribute
    if gatt_names[0] != "history":
        print(f"Error: Expected attribute name 'history', but got {gatt_names[0]}")

    # Read attribute value
    str_att = f.history

    if verbose and rank == 0:
        print("Global attribute name=", gatt_names[0]," value=",str_att)

    # Equivalently, this can also be done by using a function call
    str_att = f.get_att(gatt_names[0])

    if verbose and rank == 0:
        print("Global attribute name=", gatt_names[0]," value=",str_att)

    # Find the name of the second global attribute
    if gatt_names[1] != "digits":
        print(f"Error: Expected attribute name 'digits', but got {gatt_names[1]}")

    # Read attribute value
    short_att = f.digits

    if verbose and rank == 0:
        print("Global attribute name=", gatt_names[1]," value=",short_att)

    # Equivalently, this can also be done by using a function call
    short_att = f.get_att(gatt_names[1])

    if verbose and rank == 0:
        print("Global attribute name=", gatt_names[1]," value=",short_att)

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
        write_attr(filename, file_format)
        read_attr(filename)
    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

