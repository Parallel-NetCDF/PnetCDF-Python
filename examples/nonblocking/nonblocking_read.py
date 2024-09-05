#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
This example is the counterpart of nonblocking_write.py, but does reading
instead.  It opens the output file created by nonblocking_write.py, a netcdf
file in CDF-5 format, and reads a number of 3D integer non-record variables.

To run:
  mpiexec -n num_processes nonblocking_read.py [filename]

  All variables are partitioned among all processes in a 3D block-block-block
  fashion.
"""

import sys, os, argparse
import numpy as np
from mpi4py import MPI
import pnetcdf

def pnetcdf_io(filename):
    # Open the file for reading
    f = pnetcdf.File(filename = filename,
                     mode = 'r',
                     comm = comm,
                     info = None)

    # obtain the number of variables defined in the input file
    nvars = len(f.variables)
    if verbose and rank == 0:
        print("number of variables =", nvars)

    buf = []
    reqs = []

    for key, value in f.variables.items():

        var = value

        # print names of all variables
        if verbose and rank == 0:
            print("variable: ",key," ndim=",var.ndim)

        # obtain the number of dimensions of variable
        ndim = var.ndim

        # obtain sizes of dimensions
        dims = var.get_dims()
        if verbose and rank == 0:
            for i in range(ndim):
                print("variable ",key," dim[",i,"] name=",dims[i].name," size=",dims[i].size)

        # set up subarray access pattern
        start = np.zeros(ndim, dtype=np.int32)
        count = np.zeros(ndim, dtype=np.int32)
        gsizes = np.zeros(ndim, dtype=np.int32)

        psizes = MPI.Compute_dims(nprocs, ndim)
        start[0] = rank % psizes[0]
        start[1] = (rank // psizes[1]) % psizes[1]
        start[2] = (rank // (psizes[0] * psizes[1])) % psizes[2]

        # calculate sizes of local read buffers
        bufsize = 1
        for i in range(ndim):
            gsizes[i] = dims[i].size
            start[i] *= dims[i].size // psizes[i]
            count[i] = dims[i].size // psizes[i]
            bufsize *= count[i]

        if verbose:
            print("rank ",rank," gsizes=",gsizes," start=",start," count=",count," bufsize=",bufsize)

        # Allocate read buffer and initialize with all -1
        rbuf = np.empty(bufsize, dtype=np.int32)
        rbuf.fill(-1)
        buf.append(rbuf)

        # Read one variable at a time, using iput APIs
        req_id = var.iget_var(rbuf, start = start, count = count)
        reqs.append(req_id)

    # commit posted nonblocking requests
    errs = [None] * nvars
    f.wait_all(nvars, reqs, errs)

    # check errors
    for i in range(nvars):
        if pnetcdf.strerrno(errs[i]) != "NC_NOERR":
            print(f"Error on request {i}:",  pnetcdf.strerror(errs[i]))

    # verify contents of read buffers
    for i in range(nvars):
        for j in range(len(buf[i])):
            expect = rank * i + 123 + j
            if buf[i][j] != expect:
                print("Error: buf[",i,"][",j,"] expect ",expect," but got ",buf[i][j])
                break

    # Close the file
    f.close()


def parse_help():
    help_flag = "-h" in sys.argv or "--help" in sys.argv
    if help_flag and rank == 0:
        help_text = (
            "Usage: {} [-h | -q] [file_name]\n"
            "       [-h] Print help\n"
            "       [-q] Quiet mode (reports when fail)\n"
            "       [filename] (Optional) input netCDF file name\n"
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
    parser.add_argument("dir", nargs="?", type=str, help="(Optional) input netCDF file name",\
                         default = "testfile.nc")
    parser.add_argument("-q", help="Quiet mode (reports when fail)", action="store_true")
    args = parser.parse_args()

    verbose = False if args.q else True

    filename = args.dir

    if verbose and rank == 0:
        print("{}: example of calling nonblocking read APIs".format(os.path.basename(__file__)))

    try:
        pnetcdf_io(filename)
    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

