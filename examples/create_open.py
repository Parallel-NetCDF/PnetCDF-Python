#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
This example shows how to use `File` class constructor to create a netCDF file
and to open the file for read only.

Example commands for MPI run and outputs from running ncmpidump on the
netCDF file produced by this example program:

  % mpiexec -n 4 python3  create_open.py /tmp/test1.nc
  % ncmpidump /tmp/test1.nc
  netcdf test1 {
  // file format: CDF-1
  }
"""

import sys, os, argparse
from mpi4py import MPI
import pnetcdf

def parse_help():
    help_flag = "-h" in sys.argv or "--help" in sys.argv
    if help_flag and rank == 0:
        help_text = (
        "Usage: {} [-h] | [-q] [file_name]\n"
            "       [-h] Print help\n"
            "       [-q] Quiet mode (reports when fail)\n"
            "       [filename] (Optional) output netCDF file name\n"
        ).format(sys.argv[0])
        print(help_text)
    return help_flag

def pnetcdf_io(filename):
    if verbose and rank == 0:
        print("{}: example of file create and open".format(os.path.basename(__file__)))

    # create a new file using file clobber mode, i.e. flag "-w"
    f = pnetcdf.File(filename=filename, mode = 'w', comm=comm, info=None)

    # close the file
    f.close()

    # open the newly created file for read only
    f = pnetcdf.File(filename=filename, mode = 'r', comm=comm, info=None)

    # close the file
    f.close()


if __name__ == "__main__":
    verbose = True
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
    args = parser.parse_args()

    if args.q: verbose = False

    filename = args.dir

    try:
        pnetcdf_io(filename)
    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

