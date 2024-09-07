#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
This example prints all MPI-IO hints used.

Example commands for MPI run and outputs from running ncmpidump on the
netCDF file produced by this example program:
    % mpiexec -n 4 python3 get_info.py tmp/test1.nc
    % ncmpidump tmp/test1.nc
        Example standard output:
    MPI File Info: nkeys = 18
    MPI File Info: [ 0] key =            cb_buffer_size, value = 16777216
    MPI File Info: [ 1] key =             romio_cb_read, value = automatic
    MPI File Info: [ 2] key =            romio_cb_write, value = automatic
    MPI File Info: [ 3] key =                  cb_nodes, value = 1
    MPI File Info: [ 4] key =         romio_no_indep_rw, value = false
    MPI File Info: [ 5] key =              romio_cb_pfr, value = disable
    MPI File Info: [ 6] key =         romio_cb_fr_types, value = aar
    MPI File Info: [ 7] key =     romio_cb_fr_alignment, value = 1
    MPI File Info: [ 8] key =     romio_cb_ds_threshold, value = 0
    MPI File Info: [ 9] key =         romio_cb_alltoall, value = automatic
    MPI File Info: [10] key =        ind_rd_buffer_size, value = 4194304
    MPI File Info: [11] key =        ind_wr_buffer_size, value = 524288
    MPI File Info: [12] key =             romio_ds_read, value = automatic
    MPI File Info: [13] key =            romio_ds_write, value = automatic
    MPI File Info: [14] key =            cb_config_list, value = *:1
    MPI File Info: [15] key =      nc_header_align_size, value = 512
    MPI File Info: [16] key =         nc_var_align_size, value = 512
    MPI File Info: [17] key = nc_header_read_chunk_size, value = 0

"""

import sys, os, argparse
import numpy as np
from mpi4py import MPI
import pnetcdf

def print_info(info_used):
    nkeys = info_used.Get_nkeys()
    print("MPI File Info: nkeys =", nkeys)
    for i in range(nkeys):
        key = info_used.Get_nthkey(i)
        value = info_used.Get(key)
        print("MPI File Info: [{:2d}] key = {:25s}, value = {}".format(i, key, value))


def pnetcdf_io(filename):

    # create a new file using clobber "w" mode
    f = pnetcdf.File(filename=filename,
                     mode = 'w',
                     format = "NC_64BIT_DATA",
                     comm=comm,
                     info=None)

    # exit the define mode
    f.enddef()

    # get all the hints used
    info_used = f.inq_info()
    if verbose and rank == 0:
        print_info(info_used)

    # free info object
    info_used.Free()

    # close the file
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
        print("{}: example of getting MPI-IO hints".format(os.path.basename(__file__)))

    try:
        pnetcdf_io(filename)
    except BaseException as err:
        print("Error: type:", type(err), str(err))
        raise

    MPI.Finalize()

