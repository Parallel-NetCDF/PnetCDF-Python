#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
  This example shows how to use a single call of `Variable` method put_var() to 
  to write a sequence of requests with arbitrary array indices and lengths.
 
    To run:
        % mpiexec -n num_process python3 put_varn_int.py [test_file_name]
 
  Note that by specifying num_reqs, users can write more than one element 
  starting at each selected location.

  Example commands for MPI run and outputs from running ncmpidump on the
  output netCDF file produced by this example program:
 
     % mpiexec -n 4 python3 put_varn_int.py /tmp/test1.nc
 
     % ncmpidump /tmp/test1.nc
     netcdf test1 {
     // file format: CDF-5 (big variables)
     dimensions:
              Y = 4 ;
              X = 10 ;
     variables:
              int var(Y, X) ;
     data:
 
      var =
        3, 3, 3, 1, 1, 0, 0, 2, 1, 1,
        0, 2, 2, 2, 3, 1, 1, 2, 2, 2,
        1, 1, 2, 3, 3, 3, 0, 0, 1, 1,
        0, 0, 0, 2, 1, 1, 1, 3, 3, 3 ;
     }
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
"""

import sys
import os
from mpi4py import MPI
import pnetcdf
import argparse
import numpy as np
import inspect

verbose = True

NY = 4
NX = 10


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

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    nprocs = size
    NY = 4
    NX = 10
    NDIMS = 2
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

    if args.q:
        verbose = False
    if args.k:
        kind_dict = {'1':None, '2':"64BIT_OFFSET", '5':"64BIT_DATA"}
        file_format = kind_dict[args.k]
    filename = args.dir
    if verbose and rank == 0:
        print("{}: example of writing multiple variables in a call".format(os.path.basename(__file__)))

    # Run pnetcdf i/o
    f = pnetcdf.File(filename=filename, mode = 'w', format=file_format, comm=comm, info=None)
    dimx = f.def_dim('x',NX)
    dimy = f.def_dim('y',NY)
    v = f.def_var('var', pnetcdf.NC_INT, ('y', 'x'))
    # need 4 processes to fill the variables
    if nprocs < 4:
        f.set_fill(pnetcdf.NC_FILL)
    f.enddef()
    if rank == 0:
        num_reqs = 4
        starts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
        counts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
        starts[0][0] = 0; starts[0][1] = 5; counts[0][0] = 1; counts[0][1] = 2
        starts[1][0] = 1; starts[1][1] = 0; counts[1][0] = 1; counts[1][1] = 1
        starts[2][0] = 2; starts[2][1] = 6; counts[2][0] = 1; counts[2][1] = 2
        starts[3][0] = 3; starts[3][1] = 0; counts[3][0] = 1; counts[3][1] = 3
        # rank 0 is writing the following locations: ("-" means skip)
        #               -  -  -  -  -  0  0  -  -  - 
        #               0  -  -  -  -  -  -  -  -  - 
        #               -  -  -  -  -  -  0  0  -  - 
        #               0  0  0  -  -  -  -  -  -  - 
    elif rank == 1:
        num_reqs = 6
        starts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
        counts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
        starts[0][0] = 0; starts[0][1] = 3; counts[0][0] = 1; counts[0][1] = 2
        starts[1][0] = 0; starts[1][1] = 8; counts[1][0] = 1; counts[1][1] = 2
        starts[2][0] = 1; starts[2][1] = 5; counts[2][0] = 1; counts[2][1] = 2
        starts[3][0] = 2; starts[3][1] = 0; counts[3][0] = 1; counts[3][1] = 2
        starts[4][0] = 2; starts[4][1] = 8; counts[4][0] = 1; counts[4][1] = 2
        starts[5][0] = 3; starts[5][1] = 4; counts[5][0] = 1; counts[5][1] = 3
        # rank 1 is writing the following locations: ("-" means skip)
        #               -  -  -  1  1  -  -  -  1  1 
        #               -  -  -  -  -  1  1  -  -  - 
        #               1  1  -  -  -  -  -  -  1  1 
        #               -  -  -  -  1  1  1  -  -  - 
    elif rank == 2:
        num_reqs = 5
        starts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
        counts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
        starts[0][0] = 0; starts[0][1] = 7; counts[0][0] = 1; counts[0][1] = 1
        starts[1][0] = 1; starts[1][1] = 1; counts[1][0] = 1; counts[1][1] = 3
        starts[2][0] = 1; starts[2][1] = 7; counts[2][0] = 1; counts[2][1] = 3
        starts[3][0] = 2; starts[3][1] = 2; counts[3][0] = 1; counts[3][1] = 1
        starts[4][0] = 3; starts[4][1] = 3; counts[4][0] = 1; counts[4][1] = 1
        # rank 2 is writing the following locations: ("-" means skip)
        #         -  -  -  -  -  -  -  2  -  - 
        #         -  2  2  2  -  -  -  2  2  2 
        #         -  -  2  -  -  -  -  -  -  - 
        #         -  -  -  2  -  -  -  -  -  - 
    elif rank == 3:
        num_reqs = 4
        starts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
        counts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
        starts[0][0] = 0; starts[0][1] = 0; counts[0][0] = 1; counts[0][1] = 3
        starts[1][0] = 1; starts[1][1] = 4; counts[1][0] = 1; counts[1][1] = 1
        starts[2][0] = 2; starts[2][1] = 3; counts[2][0] = 1; counts[2][1] = 3
        starts[3][0] = 3; starts[3][1] = 7; counts[3][0] = 1; counts[3][1] = 3
        # rank 3 is writing the following locations: ("-" means skip)
        #         3  3  3  -  -  -  -  -  -  - 
        #         -  -  -  -  3  -  -  -  -  - 
        #         -  -  -  3  3  3  -  -  -  - 
        #         -  -  -  -  -  -  -  3  3  3 
    else:
        num_reqs = 0
        starts = np.zeros((num_reqs, NDIMS), dtype=np.int64)
        counts = np.zeros((num_reqs, NDIMS), dtype=np.int64)

    # allocate I/O buffer and initialize its contents
    w_len = np.sum(np.prod(counts, axis=1))
    buffer = np.full(w_len, rank, dtype=np.int32)
    # set the buffer pointers to different offsets to the I/O buffe
    v.put_var_all(buffer, start = starts, count = counts, num = num_reqs)
    f.close()

    MPI.Finalize()

if __name__ == "__main__":
    main()
