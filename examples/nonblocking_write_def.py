####################################################################
# 
#  Copyright (C) 2014, Northwestern University 
#  See COPYRIGHT notice in top-level directory.
# 
####################################################################
"""
    This example is the same as nonblocking_write.py expect all nonblocking
    write requests (calls to iput and bput) are posted in define mode.
     It creates a netcdf file in CDF-5 format and writes a number of
     3D integer non-record variables. The measured write bandwidth is reported
     at the end. Usage: (for example)

     To run:
         mpiexec -n num_processes nonblocking_write_def.py [filename] [len]
         
     where len decides the size of each local array, which is len x len x len.
     So, each non-record variable is of size len*len*len * nprocs * sizeof(int)
     All variables are partitioned among all processes in a 3D
     block-block-block fashion. Below is an example standard output from
     command:
         mpiexec -n 32 python3 nonblocking_write_def.py tmp/test1.nc -l 100
 
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

import sys
import os
from mpi4py import MPI
import pncpy
from pncpy import inq_malloc_max_size, inq_malloc_size
import argparse
import numpy as np
import inspect
from pncpy import strerror, strerrno

verbose = True

NDIMS = 3
NUM_VARS = 10


def parse_help(comm):
    rank = comm.Get_rank()
    help_flag = "-h" in sys.argv or "--help" in sys.argv
    if help_flag:
        if rank == 0:
            help_text = (
                "Usage: {} [-h] | [-q] [file_name]\n"
                "       [-h] Print help\n"
                "       [-q] Quiet mode (reports when fail)\n"
                "       [-l len] size of each dimension of the local array\n"
                "       [filename] (Optional) output netCDF file name\n"
            ).format(sys.argv[0])
            print(help_text)

    return help_flag

def print_info(info_used):

    print("MPI hint: cb_nodes        =", info_used.Get("cb_nodes"))
    print("MPI hint: cb_buffer_size  =", info_used.Get("cb_buffer_size"))
    print("MPI hint: striping_factor =", info_used.Get("striping_factor"))
    print("MPI hint: striping_unit   =", info_used.Get("striping_unit"))

def pnetcdf_check_mem_usage(comm):
    rank = comm.Get_rank()
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
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    nprocs = size
    
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
    parser.add_argument("-l", help="Size of each dimension of the local array\n")
    args = parser.parse_args()
    file_format = None
    length = 10
    if args.q:
        verbose = False
    if args.l:
        if int(args.l) > 0:
            length = int(args.l)
    filename = args.dir
    if verbose and rank == 0:
        print("{}: example of file create and open".format(__file__))

    starts = np.zeros(NDIMS, dtype=np.int32)
    counts = np.zeros(NDIMS, dtype=np.int32)
    gsizes = np.zeros(NDIMS, dtype=np.int32)
    buf = []

    psizes = MPI.Compute_dims(nprocs, NDIMS)
    starts[0] = rank % psizes[0]
    starts[1] = (rank // psizes[1]) % psizes[1]
    starts[2] = (rank // (psizes[0] * psizes[1])) % psizes[2]

    bufsize = 1
    for i in range(NDIMS):
        gsizes[i] = length * psizes[i]
        starts[i] *= length
        counts[i] = length
        bufsize *= length

    # Allocate buffer and initialize with non-zero numbers
    for i in range(NUM_VARS):
        buf.append(np.empty(bufsize, dtype=np.int32))
        for j in range(bufsize):
            buf[i][j] = rank * i + 123 + j

    comm.Barrier()
    write_timing = MPI.Wtime()

    # Create the file
    try:
        f = pncpy.File(filename=filename, mode = 'w', format = "64BIT_DATA", comm=comm, info=None)
    except OSError as e:
        print("Error at {}:{} ncmpi_create() file {} ({})".format(__file__,inspect.currentframe().f_back.f_lineno, filename, e))
        comm.Abort()
        exit(1)

    # Define dimensions
    dims = []
    for i in range(NDIMS):
        dim = f.def_dim(chr(ord('x')+i), gsizes[i])
        dims.append(dim)

    # Define variables
    vars = []
    for i in range(NUM_VARS):
        var = f.def_var("var{}".format(i), pncpy.NC_INT, dims)
        vars.append(var)


    # Write one variable at a time
    for i in range(NUM_VARS):
        vars[i].iput_var(buf[i], start = starts, count = counts)
    # Enter data mode
    f.enddef()
    f.wait_all(num = pncpy.NC_REQ_ALL)
    # Close the file

    bbufsize = bufsize * NUM_VARS * np.dtype(np.int32).itemsize
    f.attach_buff(bbufsize)
    reqs = []
    for i in range(NUM_VARS):
        req_id = vars[i].bput_var(buf[i], start = starts, count = counts)
        reqs.append(req_id)
        # can safely change contents or free up the buf[i] here
    
    # wait for the nonblocking I/O to complete
    req_errs = [None] * NUM_VARS
    f.wait_all(NUM_VARS, reqs, req_errs)

    for i in range(NUM_VARS):
        if strerrno(req_errs[i]) != "NC_NOERR":
            print(f"Error on request {i}:",  strerror(req_errs[i]))
    # detach the temporary buffer
    f.detach_buff()
    put_size = f.inq_put_size()
    # Get all the hints used
    info_used = f.inq_info()
    put_size = comm.allreduce(put_size, op=MPI.SUM)
    f.close()

    write_timing = MPI.Wtime() - write_timing

    write_size = bufsize * NUM_VARS * np.dtype(np.int32).itemsize

    for i in range(NUM_VARS):
        buf[i] = None

    sum_write_size = comm.reduce(write_size, MPI.SUM, root=0)
    max_write_timing = comm.reduce(write_timing, MPI.MAX, root=0)

    if rank == 0 and verbose:
        print()
        print("Total amount writes to variables only   (exclude header) = {} bytes".format(sum_write_size))
        print("Total amount writes reported by pnetcdf (include header) = {} bytes".format(put_size))
        print()
        subarray_size = (bufsize * np.dtype(np.int32).itemsize) / 1048576.0
        print_info(info_used)
        print("Local array size {} x {} x {} integers, size = {:.2f} MB".format(length, length, length, subarray_size))
        sum_write_size /= 1048576.0
        print("Global array size {} x {} x {} integers, write size = {:.2f} GB".format(gsizes[0], gsizes[1], gsizes[2], sum_write_size/1024.0))

        write_bw = sum_write_size / max_write_timing
        print(" procs    Global array size  exec(sec)  write(MB/s)")
        print("-------  ------------------  ---------  -----------")
        print(" {:4d}    {:4d} x {:4d} x {:4d} {:8.2f}  {:10.2f}\n".format(nprocs, gsizes[0], gsizes[1], gsizes[2], max_write_timing, write_bw))


    pnetcdf_check_mem_usage(comm)
    MPI.Finalize()

if __name__ == "__main__":
    main()
