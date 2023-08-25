####################################################################
# 
#  Copyright (C) 2014, Northwestern University 
#  See COPYRIGHT notice in top-level directory.
# 
####################################################################
"""
 This example shows how to use `Variable` class methods and `File` class methods 
 to set the fill mode of variables and fill values.
 * 1. set_fill() to enable fill mode of the file
 * 2. def_fill() to enable fill mode and define the variable's fill value
 * 3. inq_var_fill() to inquire the variable's fill mode information
 * 4. put_vara_all() to write two 2D 4-byte integer array in parallel.


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

import sys
import os
from mpi4py import MPI
import pncpy
from pncpy import inq_malloc_max_size, inq_malloc_size
import argparse
import numpy as np

verbose = True
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def parse_help():
    help_flag = "-h" in sys.argv or "--help" in sys.argv
    if help_flag:
        if rank == 0:
            help_text = (
                "Usage: {} [-h] | [-q] [file_name]\n"
                "       [-h] Print help\n"
                "       [-q] Quiet mode (reports when fail)\n"
                "       [filename] (Optional) output netCDF file name\n"
            ).format(sys.argv[0])
            print(help_text)

    return help_flag

def pnetcdf_check_mem_usage(comm):
    # global verbose
    malloc_size, sum_size = 0, 0
    # print info about PnetCDF internal malloc usage
    try:
        malloc_size = inq_malloc_max_size()
    except:
        return 
    else:
        sum_size = comm.reduce(malloc_size, MPI.SUM, root=0)
        if rank == 0 and verbose:
            print("Maximum heap memory allocated by PnetCDF internally is {} bytes".format(sum_size))
        # check if there is any PnetCDF internal malloc residue
        malloc_size = inq_malloc_size()
        sum_size = comm.reduce(malloc_size, MPI.SUM, root=0)
        if rank == 0 and sum_size > 0:
            print("Heap memory allocated by PnetCDF internally has {} bytes yet to be freed".format(sum_size))


def main():
    NY = 3
    NX = 4
    nprocs = size
    global verbose
    if parse_help():
        MPI.Finalize()
        return 1
    # get command-line arguments
    args = None
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs="?", type=str, help="(Optional) output netCDF file name",\
                         default = "testfile.nc")
    parser.add_argument("-q", help="Quiet mode (reports when fail)", action="store_true")
    
    args = parser.parse_args()
    if args.q:
        verbose = False
    filename = args.dir
    if verbose and rank == 0:
        print("{}: example of file create and open".format(__file__))
    # create a new file using "w" mode
    f = pncpy.File(filename=filename, mode = 'w', comm=comm, info=None)
    # the global array is NY * (NX * nprocs)
    global_ny = NY
    global_nx = NX * nprocs
    # define the dimensions
    dim_xu = f.def_dim('REC_DIM', -1)
    dim_x = f.def_dim('X',global_nx)
    dim_y = f.def_dim('Y',global_ny)
    # define a 2D variable of integer type
    fix_var = f.def_var("fix_var", pncpy.NC_INT, (dim_y, dim_x))
    rec_var =  f.def_var("rec_var", pncpy.NC_INT, (dim_xu, dim_x))
    # set the fill mode to NC_FILL for the entire file
    old_fillmode = f.set_fill(pncpy.NC_FILL)
    if verbose:
        if old_fillmode == pncpy.NC_FILL:
            print("The old fill mode is NC_FILL\n")
        else:
            print("The old fill mode is NC_NOFILL\n")
    # set the fill mode to back to NC_NOFILL for the entire file
    f.set_fill(pncpy.NC_NOFILL)
    # set the variable's fill mode to NC_FILL with default fill value
    fix_var.def_fill(no_fill = 0)
    # set a customized fill value -1
    fill_value = np.int32(-1)
    rec_var._FillValue = fill_value
    # exit define mode
    f.enddef()
    starts = np.array([0, NX * rank])
    counts = np.array([NY, NX])
    buf = np.array([[rank] * NX] * NY).astype('i4')
    # do not write the variable in full
    counts[1] -= 1
    fix_var.put_var_all(buf, start = starts, count = counts)
    no_fill, fill_value = fix_var.inq_fill()
    assert(no_fill == 0)
    assert(fill_value == pncpy.NC_FILL_INT)

    # fill the 1st record of the record variable
    counts[0] = 1
    rec_var.fill_rec(starts[0])
    # write to the 1st record
    rec_var.put_var_all(buf, start = starts, count = counts)
    # fill the 2nd record of the record variable
    starts[0] = 1
    rec_var.fill_rec(starts[0])
    # write to the 2nd record
    rec_var.put_var_all(buf, start = starts, count = counts)
    f.close()
    pnetcdf_check_mem_usage(comm)

if __name__ == "__main__":
    main()
