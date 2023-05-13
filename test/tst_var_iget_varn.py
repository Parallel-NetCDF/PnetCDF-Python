# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   The program runs in non-blocking mode and makes a request to read a list of subarray of 
   a netCDF variable of an opened netCDF file using iget_var method of `Variable` class. The 
   library will internally invoke ncmpi_iget_varn in C. 
"""
import pncpy
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from pncpy import strerror, strerrno
from utils import validate_nc_file

seed(0)
file_formats = ['64BIT_DATA', '64BIT_OFFSET', None]
file_name = "tst_var_iget_varn.nc"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
xdim=4; ydim=10
# max number of subarrays requested among all put requests from all ranks
MAX_NUM_REQS = 6
NDIMS = 2
# data to store in the NetCDF variable
data = np.array([[3, 3, 3, 1, 1, 0, 0, 2, 1, 1],
                 [0, 2, 2, 2, 3, 1, 1, 2, 2, 2],
                 [1, 1, 2, 3, 3, 3, 0, 0, 1, 1],
                 [0, 0, 0, 2, 1, 1, 1, 3, 3, 3]], np.float32)

starts = np.zeros((MAX_NUM_REQS, NDIMS), dtype=np.int64)
counts = np.zeros((MAX_NUM_REQS, NDIMS), dtype=np.int64)

#initialize variable values
if rank == 0:
    # number of subarrays requested for each iget_var
    num_subarray_reqs = 4
    starts[0][0] = 0; starts[0][1] = 5; counts[0][0] = 1; counts[0][1] = 2
    starts[1][0] = 1; starts[1][1] = 0; counts[1][0] = 1; counts[1][1] = 1
    starts[2][0] = 2; starts[2][1] = 6; counts[2][0] = 1; counts[2][1] = 2
    starts[3][0] = 3; starts[3][1] = 0; counts[3][0] = 1; counts[3][1] = 3
    # rank 0 is reading the following locations: ("-" means skip)
    #               -  -  -  -  -  0  0  -  -  - 
    #               0  -  -  -  -  -  -  -  -  - 
    #               -  -  -  -  -  -  0  0  -  - 
    #               0  0  0  -  -  -  -  -  -  - 
elif rank == 1:
    num_subarray_reqs = 6
    starts[0][0] = 0; starts[0][1] = 3; counts[0][0] = 1; counts[0][1] = 2
    starts[1][0] = 0; starts[1][1] = 8; counts[1][0] = 1; counts[1][1] = 2
    starts[2][0] = 1; starts[2][1] = 5; counts[2][0] = 1; counts[2][1] = 2
    starts[3][0] = 2; starts[3][1] = 0; counts[3][0] = 1; counts[3][1] = 2
    starts[4][0] = 2; starts[4][1] = 8; counts[4][0] = 1; counts[4][1] = 2
    starts[5][0] = 3; starts[5][1] = 4; counts[5][0] = 1; counts[5][1] = 3
    # rank 1 is reading the following locations: ("-" means skip)
    #               -  -  -  1  1  -  -  -  1  1 
    #               -  -  -  -  -  1  1  -  -  - 
    #               1  1  -  -  -  -  -  -  1  1 
    #               -  -  -  -  1  1  1  -  -  - 
elif rank == 2:
    num_subarray_reqs = 5
    starts[0][0] = 0; starts[0][1] = 7; counts[0][0] = 1; counts[0][1] = 1
    starts[1][0] = 1; starts[1][1] = 1; counts[1][0] = 1; counts[1][1] = 3
    starts[2][0] = 1; starts[2][1] = 7; counts[2][0] = 1; counts[2][1] = 3
    starts[3][0] = 2; starts[3][1] = 2; counts[3][0] = 1; counts[3][1] = 1
    starts[4][0] = 3; starts[4][1] = 3; counts[4][0] = 1; counts[4][1] = 1
    # rank 2 is reading the following locations: ("-" means skip)
    #         -  -  -  -  -  -  -  2  -  - 
    #         -  2  2  2  -  -  -  2  2  2 
    #         -  -  2  -  -  -  -  -  -  - 
    #         -  -  -  2  -  -  -  -  -  - 
elif rank == 3:
    num_subarray_reqs = 4
    starts[0][0] = 0; starts[0][1] = 0; counts[0][0] = 1; counts[0][1] = 3
    starts[1][0] = 1; starts[1][1] = 4; counts[1][0] = 1; counts[1][1] = 1
    starts[2][0] = 2; starts[2][1] = 3; counts[2][0] = 1; counts[2][1] = 3
    starts[3][0] = 3; starts[3][1] = 7; counts[3][0] = 1; counts[3][1] = 3
    # rank 3 is reading the following locations: ("-" means skip)
    #         3  3  3  -  -  -  -  -  -  - 
    #         -  -  -  -  3  -  -  -  -  - 
    #         -  -  -  3  3  3  -  -  -  - 
    #         -  -  -  -  -  -  -  3  3  3 
else:
    num_subarray_reqs = 0
# obtain the buffer size of returned array
buf_len = 0
for i in range(num_subarray_reqs):
    w_req_len = np.prod(counts[i,:])
    buf_len += w_req_len
# generate reference array for comparing at the testing phase
dataref = np.full((buf_len,), rank, np.float32)
# total number of iget_var requests for this test program
num_reqs = 10
# initialize a list to store references of variable values 
v_datas = []

class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        self._file_format = file_formats.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=self._file_format, comm=comm, info=None)
        dx = f.def_dim('x',xdim)
        dy = f.def_dim('y',ydim)

        # define 20 netCDF variables
        for i in range(num_reqs * 2):
            v = f.def_var(f'data{i}', pncpy.NC_FLOAT, (dx, dy))
        # initialize variable values
        f.enddef()
        for i in range(num_reqs * 2):
            v = f.variables[f'data{i}']
            v[:] = data
        f.close()
        assert validate_nc_file(self.file_path) == 0


        f = pncpy.File(self.file_path, 'r')
        # each process post 10 requests to read a list of subarrays from the variable
        req_ids = []
        v_datas.clear()
        for i in range(num_reqs):
            v = f.variables[f'data{i}']
            buff = np.empty(shape = buf_len, dtype = v.datatype)
            # post the request to read multiple slices (subarrays) of the variable
            req_id = v.iget_var(buff, start = starts, count = counts, num = num_subarray_reqs)
            # track the reqeust ID for each read reqeust 
            req_ids.append(req_id)
            # store the reference of variable values
            v_datas.append(buff)
        f.end_indep()
        # commit those 10 requests to the file at once using wait_all (collective i/o)
        req_errs = [None] * num_reqs
        f.wait_all(num_reqs, req_ids, req_errs)
        # check request error msg for each unsuccessful requests
        for i in range(num_reqs):
            if strerrno(req_errs[i]) != "NC_NOERR":
                print(f"Error on request {i}:",  strerror(req_errs[i]))
        
         # post 10 requests to read an array of values for the last 10 variables w/o tracking req ids
        for i in range(num_reqs, num_reqs * 2):
            v = f.variables[f'data{i}']
            buff = np.empty(buf_len, dtype = v.datatype)
            # post the request to read a list of subarrays from the variable
            v.iget_var(buff, start = starts, count = counts, num = num_subarray_reqs)
            # store the reference of variable values
            v_datas.append(buff)
        
        # commit all pending get requests to the file at once using wait_all (collective i/o)
        req_errs = f.wait_all(num = pncpy.NC_GET_REQ_ALL)
        f.close()
        assert validate_nc_file(self.file_path) == 0
    
    def tearDown(self):
        # remove the temporary files if the test file directory is not specified
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def runTest(self):
        """testing variable iget varn method for CDF-5/CDF-2/CDF-1 file format"""
        # test iget_varn and collective i/o wait_all
        for i in range(num_reqs * 2):
            assert_array_equal(v_datas[i], dataref)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
