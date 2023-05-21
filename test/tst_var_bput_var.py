# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API. The program runs 
   in non-blocking mode and makes a request to write all the values of a variable into a netCDF variable
   of an opened netCDF file using bput_var method of `Variable` class. This method is a buffered version 
   of iput_var and requires the user to attach an internal buffer of size equal to the sum of all requests 
   using attach_buff method of `File` class. The library will internally invoke ncmpi_bput_var and 
   ncmpi_attach_buffer in C. 
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
file_name = "tst_var_bput_var.nc"
xdim=9; ydim=10; zdim=11
data = randint(0,10, size=(xdim,ydim,zdim)).astype('i4')
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
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
        f.def_dim('y',ydim)
        f.def_dim('z',zdim)
        # estimate the memory buffer size of all requests and attach buffer for buffered put requests
        buffsize = num_reqs * data.nbytes
        f.attach_buff(buffsize)
        assert(f.inq_buff_size() == buffsize)
        # define 20 netCDF variables
        for i in range(2 * num_reqs):
            v = f.def_var(f'data{i}', pncpy.NC_INT, ('x','y','z'))

        # post 10 requests to write the whole variable for the first 10 variables
        f.enddef()
        req_ids = []
        # check the usage of write buffer in memory
        print(f"Buffer check: internal buffer has {f.inq_buff_size() - f.inq_buff_usage()} bytes left")
        for i in range(num_reqs):
            v = f.variables[f'data{i}']
            # post the request to write the whole variable 
            req_id = v.bput_var(data)
            # track the reqeust ID for each write reqeust 
            req_ids.append(req_id)
        # check the usage of write buffer in memory
        print(f"Buffer check: internal buffer has {f.inq_buff_size() - f.inq_buff_usage()} bytes left")
        f.end_indep()
        # all processes commit those 10 requests to the file at once using wait_all (collective i/o)
        req_errs = [None] * num_reqs
        f.wait_all(num_reqs, req_ids, req_errs)
        # comm.Barrier()
        # check request error msg for each unsuccessful requests
        for i in range(num_reqs):
            if strerrno(req_errs[i]) != "NC_NOERR":
                print(f"Error on request {i}:",  strerror(req_errs[i]))

        # check the usage of write buffer in memory
        print(f"Buffer check: internal buffer has {f.inq_buff_size() - f.inq_buff_usage()} bytes left")

        # w/o tracking request id: post 10 requests to write the whole variable for the last 10 variables
        for i in range(num_reqs, 2 * num_reqs):
            v = f.variables[f'data{i}']
            # post the request to write the whole variable without tracking id
            v.bput_var(data)
        
        # check the usage of write buffer in memory
        print(f"Buffer check: internal buffer has {f.inq_buff_size() - f.inq_buff_usage()} bytes left")
        # all processes commit all pending put requests to the file at once using wait_all (collective i/o)
        f.wait_all(num = pncpy.NC_PUT_REQ_ALL)
        # relase the internal buffer
        f.detach_buff()
        f.close()
        assert validate_nc_file(self.file_path) == 0
    
    def tearDown(self):
        # remove the temporary files
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def runTest(self):
        """testing variable bput var all for CDF-5/CDF-2/CDF-1 file format"""

        f = pncpy.File(self.file_path, 'r')
        # test bput_var and collective i/o wait_all
        for i in range(2 * num_reqs):
            v = f.variables[f'data{i}']
            assert_array_equal(v[:], data)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
