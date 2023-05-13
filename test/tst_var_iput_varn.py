# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API. The program
   runs in non-blocking mode and makes a request to write a list of subarray of values to a variable 
   into a netCDF variable of an opened netCDF file using iput_var method of `Variable` class. The 
   library will internally invoke ncmpi_iput_varn in C. 
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
file_name = "tst_var_iput_varn.nc"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
xdim = 4
ydim = 10

# max number of subarrays requested among all iput requests from all ranks
max_num_subarray = 6
ndims = 2

starts = np.zeros((max_num_subarray, ndims), dtype=np.int64)
counts = np.zeros((max_num_subarray, ndims), dtype=np.int64)

# initialize variable values
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

# reference data for size >=4 (rank 0 - 3 all participated)
dataref = np.array([[3, 3, 3, 1, 1, 0, 0, 2, 1, 1],
                    [0, 2, 2, 2, 3, 1, 1, 2, 2, 2],
                    [1, 1, 2, 3, 3, 3, 0, 0, 1, 1],
                    [0, 0, 0, 2, 1, 1, 1, 3, 3, 3]], np.float32)


# reference data for 1<=size<=3
dataref[dataref >= size] = -1
# total number of put requests for the test programs
num_reqs = 10

# allocate write buffer
buf_len = 0
for i in range(num_subarrays):
    w_req_len = np.prod(counts[i,:])
    buf_len += w_req_len
data = np.empty(buf_len, dtype=np.float32)
data.fill(rank)

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
            v[:] = np.full((xdim, ydim), -1, dtype=np.float32)

        # each process post 10 requests to write an array of values
        req_ids = []
        for i in range(num_reqs):
            v = f.variables[f'data{i}']
            # post the request to write an array of values
            req_id = v.iput_var(data, start = starts, count = counts, num = num_subarrays)
            # track the reqeust ID for each write reqeust 
            req_ids.append(req_id)
        f.end_indep()
        # all processes commit those 10 requests to the file at once using wait_all (collective i/o)
        req_errs = [None] * num_reqs
        f.wait_all(num_reqs, req_ids, req_errs)
        # check request error msg for each unsuccessful requests
        for i in range(num_reqs):
            if strerrno(req_errs[i]) != "NC_NOERR":
                print(f"Error on request {i}:",  strerror(req_errs[i]))
        
         # post 10 requests to write an array of values for the last 10 variables w/o tracking req ids
        for i in range(num_reqs, num_reqs * 2):
            v = f.variables[f'data{i}']
            # post the request to write an array of values
            v.iput_var(data, start = starts, count = counts, num = num_subarrays)
        
        # all processes commit all pending requests to the file at once using wait_all (collective i/o)
        f.wait_all(num = pncpy.NC_PUT_REQ_ALL)
        f.close()
        assert validate_nc_file(self.file_path) == 0
    
    def tearDown(self):
        # remove the temporary files if the test file ouptut directory not specified
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def runTest(self):
        """testing variable iput varn for CDF-5/CDF-2/CDF-1 file format"""

        f = pncpy.File(self.file_path, 'r')
        # test iput_varn and collective i/o wait_all
        for i in range(num_reqs * 2):
            v = f.variables[f'data{i}']
            assert_array_equal(v[:], dataref)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
