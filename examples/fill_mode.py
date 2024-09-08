#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
This example shows how to use `Variable` class methods and `File` class methods
to set the fill mode of variables and fill values.
 * 1. set_fill() to enable fill mode of the file
 * 2. def_fill() to enable fill mode and define the variable's fill value
 * 3. inq_var_fill() to inquire the variable's fill mode information
 * 4. put_var_all() to write two 2D 4-byte integer array in parallel.

Example commands for MPI run and outputs from running ncmpidump on the
netCDF file produced by this example program:

  % mpiexec -n 4 python3 fill_mode.py tmp/test1.nc
  % ncmpidump tmp/test1.nc
    netcdf test1 {
    // file format: CDF-1
    dimensions:
            REC_DIM = UNLIMITED ; // (2 currently)
            X = 16 ;
            Y = 3 ;
    variables:
            int rec_var(REC_DIM, X) ;
                rec_var:_FillValue = -1 ;
            int fix_var(Y, X) ;
    data:

    rec_var =
           0, 0, 0, _, 1, 1, 1, _, 2, 2, 2, _, 3, 3, 3, _,
           0, 0, 0, _, 1, 1, 1, _, 2, 2, 2, _, 3, 3, 3, _ ;

    fix_var =
           0, 0, 0, _, 1, 1, 1, _, 2, 2, 2, _, 3, 3, 3, _,
           0, 0, 0, _, 1, 1, 1, _, 2, 2, 2, _, 3, 3, 3, _,
           0, 0, 0, _, 1, 1, 1, _, 2, 2, 2, _, 3, 3, 3, _ ;
    }

"""

import sys, os, argparse
import numpy as np
from mpi4py import MPI
import pnetcdf

def pnetcdf_io(filename):

    NY = 3
    NX = 4

    if verbose and rank == 0:
        print("Y dimension size = ", NY)
        print("X dimension size = ", NX)

    # create a new file using clobber "w" mode
    f = pnetcdf.File(filename = filename,
                     mode = 'w',
                     comm = comm,
                     info = None)

    # the global array is NY * (NX * nprocs)
    global_ny = NY
    global_nx = NX * nprocs

    # define dimensions
    time = f.def_dim('REC_DIM', -1)
    dim_x = f.def_dim('X',global_nx)
    dim_y = f.def_dim('Y',global_ny)

    # define 2D variables of integer type
    fix_var = f.def_var("fix_var", pnetcdf.NC_INT, (dim_y, dim_x))
    rec_var = f.def_var("rec_var", pnetcdf.NC_INT, (time, dim_x))

    # set the fill mode to NC_FILL for the entire file
    old_fillmode = f.set_fill(pnetcdf.NC_FILL)
    if verbose:
        if old_fillmode == pnetcdf.NC_FILL:
            print("The old fill mode is NC_FILL\n")
        else:
            print("The old fill mode is NC_NOFILL\n")

    # set the fill mode to back to NC_NOFILL for the entire file
    f.set_fill(pnetcdf.NC_NOFILL)

    # set the variable's fill mode to NC_FILL with default fill value
    fix_var.def_fill(no_fill = 0)

    # set a customized fill value -1
    fill_value = np.int32(-1)
    rec_var._FillValue = fill_value

    # exit define mode
    f.enddef()

    # set subarray access pattern
    start = np.array([0, NX * rank])
    count = np.array([NY, NX])

    if verbose:
        print("rank: ", rank," global_ny=",global_ny," global_nx=",global_nx," start=",start," count=",count)

    # allocate user buffer
    buf = np.array([[rank] * NX] * NY).astype('i4')
    for i in range(NY):
        for j in range(NX):
            buf[i, j] = 10 + rank*10 + i * NX + j

    # do not write the variable in full
    count[1] -= 1

    # write using Python style subarray access
    end = np.add(start, count)
    fix_var[start[0]:end[0], start[1]:end[1]] = buf[0:count[0], 0:count[1]]

    # Equivalently, below uses function call
    fix_var.put_var_all(buf[0:count[0], 0:count[1]], start = start, count = count)

    # check fill value
    no_fill, fill_value = fix_var.inq_fill()
    assert(no_fill == 0)
    assert(fill_value == pnetcdf.NC_FILL_INT)

    # fill the 1st record of the record variable
    count[0] = 1
    rec_var.fill_rec(start[0])

    # write to the 1st record, using Python style subarray access
    end = np.add(start, count)
    rec_var[start[0]:end[0], start[1]:end[1]] = buf[0:count[0], 0:count[1]]

    # Equivalently, below uses function call
    rec_var.put_var_all(buf[0:count[0], 0:count[1]], start = start, count = count)

    # fill the 2nd record of the record variable
    start[0] = 1
    rec_var.fill_rec(start[0])

    # write to the 2nd record using Python style subarray access
    end = np.add(start, count)
    rec_var[start[0]:end[0], start[1]:end[1]] = buf[0:count[0], 0:count[1]]

    # Equivalently, below uses function call
    rec_var.put_var_all(buf[0:count[0], 0:count[1]], start = start, count = count)

    # close file
    f.close()


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

    verbose = False if args.q else True

    filename = args.dir

    if verbose and rank == 0:
        print("{}: example of setting fill mode".format(os.path.basename(__file__)))

    try:
        pnetcdf_io(filename)
    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

