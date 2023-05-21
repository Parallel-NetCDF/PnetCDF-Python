# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   The program runs in non-blocking mode and makes a request to write an subsampled array of values
   to a variable into a netCDF variable of an opened netCDF file using bput_var method of `Variable` 
   class. This method is a buffered version of bput_var and requires the user to attach an internal 
   buffer of size equal to the sum of all requests using attach_buff method of `File` class. The 
   library will internally invoke ncmpi_bput_var and ncmpi_attach_buffer in C. 
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
file_name = "tst_var_bput_vars.nc"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
xdim=9; ydim=10; zdim=size*10
# initial values for netCDF variable
data = np.zeros((xdim,ydim,zdim)).astype('i4')
# new array that will be written using bput_var (overwriting some parts of initial values)
datam = randint(0,10, size=(1,3,5)).astype('i4')
# reference array for comparison in the testing phase
datares1, datares2 = data.copy(), data.copy()

for i in range(size):
    datares1[3:4:1,0:6:2,i*10:(i+1)*10:2] = datam
# number of put requests planning to post
num_reqs = 10
class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        self._file_format = file_formats.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=self._file_format, comm=comm, info=None)
        f.def_dim('x',xdim)
        f.def_dim('xu',-1)
        f.def_dim('y',ydim)
        f.def_dim('z',zdim)
        # estimate the memory buffer size of all requests and attach buffer for buffered put requests
        buffsize = num_reqs * datam.nbytes
        f.attach_buff(buffsize)
        assert(f.inq_buff_size() == buffsize)
        # define 20 netCDF variables
        for i in range(num_reqs * 2):
            v = f.def_var(f'data{i}', pncpy.NC_INT, ('xu','y','z'))
        # initialize variable values
        f.enddef()
        for i in range(num_reqs * 2):
            v = f.variables[f'data{i}']
            v[:] = data

        # each process post 10 requests to write a subsampled array of values
        req_ids = []
        # check the usage of write buffer in memory
        print(f"Buffer check: internal buffer has {f.inq_buff_size() - f.inq_buff_usage()} bytes left")
        starts = np.array([3, 0, 10 * rank])
        counts = np.array([1, 3, 5])
        strides = np.array([1, 2, 2])
        for i in range(num_reqs):
            v = f.variables[f'data{i}']
            # post the request to write a subsampled array of values
            req_id = v.bput_var(datam, start = starts, count = counts, stride = strides)
            # track the reqeust ID for each write reqeust 
            req_ids.append(req_id)
        # check the usage of write buffer in memory
        print(f"Buffer check: internal buffer has {f.inq_buff_size() - f.inq_buff_usage()} bytes left")
        f.end_indep()
        # all processes commit those 10 requests to the file at once using wait_all (collective i/o)
        req_errs = [None] * num_reqs
        f.wait_all(num_reqs, req_ids, req_errs)
        # check request error msg for each unsuccessful requests
        for i in range(num_reqs):
            if strerrno(req_errs[i]) != "NC_NOERR":
                print(f"Error on request {i}:",  strerror(req_errs[i]))
        
         # post 10 requests to write a subsampled arrays of values for the last 10 variables w/o tracking req ids
        for i in range(num_reqs, num_reqs * 2):
            v = f.variables[f'data{i}']
            # post the request to write a subsampled array of values
            v.bput_var(datam, start = starts, count = counts, stride = strides)
        # check the usage of write buffer in memory
        print(f"Buffer check: internal buffer has {f.inq_buff_size() - f.inq_buff_usage()} bytes left")
        # all processes commit all pending requests to the file at once using wait_all (collective i/o)
        f.wait_all(num = pncpy.NC_PUT_REQ_ALL)
        # check the usage of write buffer in memory
        print(f"Buffer check: internal buffer has {f.inq_buff_size() - f.inq_buff_usage()} bytes left")
        # relase the internal buffer
        f.detach_buff()
        f.close()
        assert validate_nc_file(self.file_path) == 0

    def runTest(self):
        """testing variable bput vars for CDF-5/CDF-2/CDF-1 file format"""

        f = pncpy.File(self.file_path, 'r')
        # test bput vars and collective i/o wait_all
        for i in range(num_reqs * 2):
            v = f.variables[f'data{i}']
            assert_array_equal(v[:], datares1)

    def tearDown(self):
        # remove the temporary file if test file directory not specified
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
