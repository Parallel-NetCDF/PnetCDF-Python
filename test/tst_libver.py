#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
This program test the followings:
    pnetcdf class member: __version__    a string of PnetCDF-Python version
    pnetcdf method: libver()             a function call to get the version
    pnetcdf method: inq_clibvers()       a string of PnetCDF-C library version
"""

import sys, argparse
from mpi4py import MPI
import pnetcdf

def parse_help():
    help_flag = "-h" in sys.argv or "--help" in sys.argv
    if help_flag and rank == 0:
        help_text = (
            "Usage: {} [-h | -q]\n"
            "       [-h] Print help\n"
            "       [-q] Quiet mode (reports when fail)\n"
        ).format(sys.argv[0])
        print(help_text)
    return help_flag

if __name__ == "__main__":

    rank = MPI.COMM_WORLD.Get_rank()

    if parse_help():
        MPI.Finalize()
        sys.exit(1)

    # Get command-line arguments
    args = None
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", help="Quiet mode (reports when fail)", action="store_true")
    args = parser.parse_args()

    verbose = False if args.q else True

    if verbose and rank == 0:
        print("test pnetcdf.libver() and pnetcdf.inq_clibvers()")

    # Run tests
    try:
        mlibver = pnetcdf.__version__
        if verbose and rank == 0:
            print("Test python class member, pnetcdf.__version__ = ", mlibver)

        plibver = pnetcdf.libver()
        if verbose and rank == 0:
            print("test pnetcdf.libver(), PnetCDF Python version : ", plibver)

        clibvers = pnetcdf.inq_clibvers()
        if verbose and rank == 0:
            print("test pnetcdf_python_clibvers(), PnetCDF C library version: ", clibvers)

    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

