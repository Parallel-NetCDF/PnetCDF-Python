#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
This example mimics the coll_perf.c from ROMIO. It creates a netcdf file and
writes a number of 3D integer non-record variables. The measured write
bandwidth is reported at the end.
To run:
  % mpiexec -n num_process python3 collective_write.py [test_file_name] [-l len]
where len decides the size of each local array, which is len x len x len.
So, each non-record variable is of size len*len*len * nprocs * sizeof(int)
All variables are partitioned among all processes in a 3D block-block-block
fashion.

Example commands for MPI run and outputs from running ncmpidump on the
netCDF file produced by this example program:
    % mpiexec -n 32 python3 collective_write.py tmp/test1.nc -l 100
    % ncmpidump tmp/test1.nc

    Example standard output:
    MPI hint: cb_nodes        = 2
    MPI hint: cb_buffer_size  = 16777216
    MPI hint: striping_factor = 32
    MPI hint: striping_unit   = 1048576
    Local array size 100 x 100 x 100 integers, size = 3.81 MB
    Global array size 400 x 400 x 200 integers, write size = 0.30 GB
     procs    Global array size  exec(sec)  write(MB/s)
     -------  ------------------  ---------  -----------
        32     400 x  400 x  200     6.67       45.72
"""

import sys, os, argparse
import numpy as np
from mpi4py import MPI
import pnetcdf

def pnetcdf_io(filename, file_format, length):
    # number of dimensions
    NDIMS = 3
    # number of variables
    NUM_VARS = 10

    if verbose and rank == 0:
        print("Number of variables = ", NUM_VARS)
        print("Number of dimensions = ", NDIMS)

    start  = np.zeros(NDIMS, dtype=np.int32)
    count  = np.zeros(NDIMS, dtype=np.int32)
    gsizes = np.zeros(NDIMS, dtype=np.int32)
    buf = []

    # calculate local subarray access pattern
    psizes = MPI.Compute_dims(nprocs, NDIMS)
    start[0] = rank % psizes[0]
    start[1] = (rank // psizes[1]) % psizes[1]
    start[2] = (rank // (psizes[0] * psizes[1])) % psizes[2]

    bufsize = 1
    for i in range(NDIMS):
        gsizes[i] = length * psizes[i]
        start[i] *= length
        count[i]  = length
        bufsize  *= length

    end = np.add(start, count)

    # Allocate buffer and initialize with non-zero numbers
    for i in range(NUM_VARS):
        buf.append(np.empty(bufsize, dtype=np.int32))
        for j in range(bufsize):
            buf[i][j] = rank * i + 123 + j

    # Create the file using file clobber mode
    f = pnetcdf.File(filename = filename,
                     mode = 'w',
                     format = file_format,
                     comm = comm,
                     info = None)

    # Define dimensions
    dims = []
    for i in range(NDIMS):
        dim = f.def_dim(chr(ord('x')+i), gsizes[i])
        dims.append(dim)

    # Define variables
    vars = []
    for i in range(NUM_VARS):
        var = f.def_var("var{}".format(i), pnetcdf.NC_INT, dims)
        vars.append(var)

    # Exit the define mode
    f.enddef()

    # Get the MPI-IO hint objects, which containing all hints used
    info_used = f.inq_info()

    # Collectively write one variable at a time
    for i in range(NUM_VARS):
        # write using Python style subarray access
        vars[i][start[0]:end[0], start[1]:end[1], start[2]:end[2]] = buf[i]

        # Equivalently, below uses function call
        vars[i].put_var_all(buf[i], start = start, count = count)

    # Close the file
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

    # Get command-line arguments
    args = None
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs="?", type=str, help="(Optional) output netCDF file name",\
                         default = "testfile.nc")
    parser.add_argument("-q", help="Quiet mode (reports when fail)", action="store_true")
    parser.add_argument("-k", help="File format: 1 for CDF-1, 2 for CDF-2, 5 for CDF-5")
    parser.add_argument("-l", help="Size of each dimension of the local array\n")
    args = parser.parse_args()

    verbose = False if args.q else True

    file_format = None
    if args.k:
        kind_dict = {'1':None, '2':"NC_64BIT_OFFSET", '5':"NC_64BIT_DATA"}
        file_format = kind_dict[args.k]

    length = 10
    if args.l and int(args.l) > 0:
        length = int(args.l)

    filename = args.dir

    if verbose and rank == 0:
        print("{}: example of collective writes".format(os.path.basename(__file__)))

    # Run I/O
    try:
        pnetcdf_io(filename, file_format, length)
    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

