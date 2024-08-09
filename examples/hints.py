#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
This example sets two PnetCDF hints: `nc_header_align_size` and
`nc_var_align_size` and prints the hint values as well as the header size,
header extent, and two variables' starting file offsets.

Example commands for MPI run and outputs from running ncmpidump on the
netCDF file produced by this example program:

  % mpiexec -n 4 python3 hints.py tmp/test1.nc
  % ncmpidump tmp/test1.nc

    Example standard output:
    nc_header_align_size      set to = 1024
    nc_var_align_size         set to = 512
    nc_header_read_chunk_size set to = 256
    header size                      = 156
    header extent                    = 1024
    var_zy start file offset         = 1024
    var_yx start file offset         = 1536

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
            "       [filename] (Optional) output netCDF file name\n"
        ).format(sys.argv[0])
        print(help_text)
    return help_flag

def print_hints(nc_file, nc_var1, nc_var2):
    value = np.zeros(MPI.MAX_INFO_VAL, dtype='c')
    header_size, header_extent, var_zy_start, var_yx_start = -1, -1, -1, -1
    h_align, v_align, h_chunk = -1, -1, -1
    info_used = MPI.INFO_NULL

    # Get header size, header extent, and variable offsets
    header_size = nc_file.inq_header_size()
    header_extent = nc_file.inq_header_extent()
    var_zy_start = nc_var1.inq_offset()
    var_yx_start = nc_var2.inq_offset()

    # Get hints from file info
    info_used = nc_file.inq_info()
    if info_used != MPI.INFO_NULL:
        value = info_used.Get("nc_header_align_size")
        if value is not None:
            h_align = int(value)
        value = info_used.Get("nc_var_align_size")
        if value is not None:
            v_align = int(value)
        value = info_used.Get("nc_header_read_chunk_size")
        if value is not None:
            h_chunk = int(value)
        info_used.Free()

    if h_align == -1:
        print("nc_header_align_size      is NOT set")
    else:
        print(f"nc_header_align_size      set to = {h_align:d}")

    if v_align == -1:
        print("nc_var_align_size         is NOT set")
    else:
        print(f"nc_var_align_size         set to = {v_align:d}")

    if h_chunk == -1:
        print("nc_header_read_chunk_size is NOT set")
    else:
        print(f"nc_header_read_chunk_size set to = {h_chunk:d}")

    print(f"header size                      = {header_size:d}")
    print(f"header extent                    = {header_extent:d}")
    print(f"var_zy start file offset         = {var_zy_start:d}")
    print(f"var_yx start file offset         = {var_yx_start:d}")

def pnetcdf_io(filename):
    NY = 5
    NX = 5
    NZ = 5

    if verbose and rank == 0:
        print("Z dimension size = ", NZ)
        print("Y dimension size = ", NY)
        print("X dimension size = ", NX)

    # create MPI info object and set a few hints
    info = MPI.Info.Create()
    info.Set("nc_header_align_size", "1024")
    info.Set("nc_var_align_size", "512")
    info.Set("nc_header_read_chunk_size", "256")

    # create a new file for writing
    f = pnetcdf.File(filename = filename,
                     mode = 'w',
                     format = "NC_64BIT_DATA",
                     comm = comm,
                     info = info)

    # define dimensions
    dim_z = f.def_dim('Z', NZ*nprocs)
    dim_y = f.def_dim('Y', NY*nprocs)
    dim_x = f.def_dim('x', NX*nprocs)

    # define a variable of size (NZ * nprocs) * (NY * nprocs)
    var_zy = f.def_var("var_zy", pnetcdf.NC_INT, (dim_z, dim_y))
    # define a variable of size (NY * nprocs) * (NX * nprocs)
    var_yx =  f.def_var("var_yx", pnetcdf.NC_FLOAT, (dim_y, dim_x))

    # exit the define mode
    f.enddef()

    # var_zy is partitioned along Z dimension
    buf_zy = np.empty(shape = (NZ * NY * nprocs, ), dtype = "i4")
    for i in range(NZ*NY*nprocs):
        buf_zy[i] = i

    # set subarray access pattern
    start = [NZ * rank, 0]
    count =[NZ, NY * nprocs]

    # write to variable
    var_zy.put_var_all(buf_zy, start = start, count = count)

    # var_yx is partitioned along X dimension
    buf_yx = np.empty(shape = (NX * NY * nprocs, ), dtype = "f4")
    for i in range(NX*NY*nprocs):
        buf_yx[i] = i

    # set subarray access pattern
    start = [0, NX*rank]
    count =[NY * nprocs, NX]

    # write to variable
    var_yx.put_var_all(buf_yx, start = start, count = count)

    if verbose and rank == 0:
        print_hints(f, var_zy, var_yx)
    info.Free()

    # close the file
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
    args = parser.parse_args()

    verbose = False if args.q else True

    filename = args.dir

    if verbose and rank == 0:
        print("{}: example of set/get PnetCDF hints".format(os.path.basename(__file__)))

    try:
        pnetcdf_io(filename)
    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

