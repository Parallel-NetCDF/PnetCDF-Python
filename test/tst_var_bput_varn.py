#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
This example program is intended to illustrate the use of the pnetCDF python
API. The program runs in non-blocking mode and makes a request to write a list
of subarray of values to a variable into a netCDF variable of an opened netCDF
file using bput_var method of `Variable` class. This method is a buffered
version of bput_var and requires the user to attach an internal buffer of size
equal to the sum of all requests using attach_buff method of `File` class. The
library will internally invoke ncmpi_bput_vara and ncmpi_attach_buffer in C.
"""

import numpy as np
from mpi4py import MPI
import os, sys

import pnetcdf
from utils import validate_nc_file

def run_test(format):

    verbose = False

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nprocs = comm.Get_size()

    # dimension sizes
    ndims = 2
    ydim = 4
    xdim = 10

    # allocate and initialize access patterns
    max_num_subarray = 6
    starts = np.zeros((max_num_subarray, ndims), dtype=np.int64)
    counts = np.zeros((max_num_subarray, ndims), dtype=np.int64)

    # only the first 4 ranks have non-zero access amount
    if rank == 0:
        # number of subarrays to request for each process
        num_subarrays = 4
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
        num_subarrays = 6
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
        num_subarrays = 5
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
        num_subarrays = 4
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
        num_subarrays = 0

    # expected contents of variables created in the file
    dataref = np.array([[3, 3, 3, 1, 1, 0, 0, 2, 1, 1],
                        [0, 2, 2, 2, 3, 1, 1, 2, 2, 2],
                        [1, 1, 2, 3, 3, 3, 0, 0, 1, 1],
                        [0, 0, 0, 2, 1, 1, 1, 3, 3, 3]], np.float32)

    # total number of variables to be defined
    num_vars = 20

    # number of bput requests
    num_reqs = num_vars // 2 if rank < 4 else 0

    # allocate write buffer
    buf_len = 0
    for i in range(num_subarrays):
        w_req_len = np.prod(counts[i,:])
        buf_len += w_req_len
    data = np.empty(buf_len, dtype=np.float32)
    data.fill(rank)

    # construct output file name
    file_name = "tst_var_bput_varn"
    if format == '64BIT_DATA':
        file_ext = ".nc5"
    elif format == '64BIT_OFFSET':
        file_ext = ".nc2"
    else:
        file_ext = ".nc"

    if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
        name = os.path.join(sys.argv[1], file_name)
        file_path = name + file_ext
    else:
        file_path = file_name + file_ext

    if verbose and rank == 0:
        print("output file name: ", file_path)

    # create a new file with selected file format
    f = pnetcdf.File(filename=file_path, mode = 'w', format=format, comm=comm, info=None)

    # define dimensions
    dy = f.def_dim('y',ydim)
    dx = f.def_dim('x',xdim)

    if verbose and rank == 0:
        print("define dimensions Y and X of sizes: ", ydim, ", ", xdim)

    # estimate the buffer size to be used in buffered put requests
    buffsize = num_reqs * data.nbytes
    if buffsize > 0:
        f.attach_buff(buffsize)
        # check the size of attached buffer
        assert(f.inq_buff_size() == buffsize)

    # define netCDF variables
    for i in range(num_vars):
        v = f.def_var(f'data{i}', pnetcdf.NC_FLOAT, (dy, dx))

    if verbose and rank == 0:
        print("define ", num_vars, " variables of type NC_FLOAT")

    # leave define mode
    f.enddef()

    # initialize contents of write buffers
    for i in range(num_vars):
        v = f.variables[f'data{i}']
        v[:] = np.full((ydim, xdim), -1, dtype=np.float32)

    # each process post num_reqs requests to write
    req_ids = []
    for i in range(num_reqs):
        v = f.variables[f'data{i}']
        assert(f.inq_buff_size() - f.inq_buff_usage() > 0)
        # post the request to write an array of values
        req_id = v.bput_var(data, start = starts, count = counts, num = num_subarrays)
        # track the request ID for each write request
        req_ids.append(req_id)

    # commit the posted requests all at once using wait_all (collective i/o)
    req_errs = [None] * num_reqs
    f.wait_all(num_reqs, req_ids, req_errs)

    # check request error msg for each unsuccessful requests
    for i in range(num_reqs):
        if pnetcdf.strerrno(req_errs[i]) != "NC_NOERR":
            print(f"Error on request {i}:",  pnetcdf.strerror(req_errs[i]))

    # post requests to write the 2nd half of variables w/o tracking req ids
    for i in range(num_reqs):
        v = f.variables[f'data{num_reqs + i}']
        v.bput_var(data, start = starts, count = counts, num = num_subarrays)

    # commit the posted requests all at once using wait_all (collective i/o)
    f.wait_all(num = pnetcdf.NC_PUT_REQ_ALL)

    # release the internal buffer
    if buffsize > 0:
        f.detach_buff()

    # close the file
    f.close()

    if rank == 0:
        if verbose:
            print("check if the newly created file is a valid NetCDF file")
        if os.environ.get('PNETCDF_DIR') is not None:
            assert validate_nc_file(os.environ.get('PNETCDF_DIR'), file_path) == 0

        if nprocs >= 4:
            if verbose:
                print("check if the file contents are expected")
            f = pnetcdf.File(file_path, 'r', comm=MPI.COMM_SELF)
            for i in range(num_vars):
                v = f.variables[f'data{i}']
                np.testing.assert_array_equal(v[:], dataref)
            f.close()

if __name__ == '__main__':
    # test CDF-1, CDF-2, CDF-5 classic NetCDF file formats
    file_formats = ['NC_64BIT_DATA', 'NC_64BIT_OFFSET', None]
    for i in range(len(file_formats)):
        try:
            run_test(file_formats[i])
        except BaseException as err:
            print("Error: type:", type(err), str(err))
            raise
