# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   The program runs in non-blocking mode and makes a request to write an array of values to a variable 
   into a netCDF variable of an opened netCDF file using iput_var method of `Variable` class. The 
   library will internally invoke ncmpi_iput_vara in C. 
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
data_models = ['64BIT_DATA', '64BIT_OFFSET', None]
file_name = "tst_var_iput_vara.nc"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
xdim=9; ydim=10; zdim=size*10
# initial values for netCDF variable
data = np.zeros((xdim,ydim,zdim)).astype('i4')
# new array that will be written using iput_var (overwriting some parts of initial values)
datam = randint(0,10, size=(1,5,10)).astype('i4')
# reference array for comparison in the testing phase
datares1, datares2 = data.copy(), data.copy()

for i in range(size):
    datares1[3:4,:5,i*10:(i+1)*10] = datam


num_reqs = 10

class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        data_model = data_models.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=data_model, Comm=comm, Info=None)
        f.def_dim('x',xdim)
        f.def_dim('xu',-1)
        f.def_dim('y',ydim)
        f.def_dim('z',zdim)



        # define 20 netCDF variables
        for i in range(num_reqs * 2):
            v = f.def_var(f'data{i}', pncpy.NC_INT, ('xu','y','z'))
        # initialize variable values
        f.enddef()
        for i in range(num_reqs * 2):
            v = f.variables[f'data{i}']
            v[:] = data

        # each process post 10 requests to write an array of values
        req_ids = []
        starts = np.array([3, 0, 10 * rank])
        counts = np.array([1, 5, 10])
        for i in range(num_reqs):
            v = f.variables[f'data{i}']
            # post the request to write an array of values
            req_id = v.iput_var(datam, start = starts, count = counts)
            # track the reqeust ID for each write reqeust 
            req_ids.append(req_id)
        f.end_indep()
        # all processes commit those 10 requests to the file at once using wait_all (collective i/o)
        req_errs = [None] * 10
        f.wait_all(num_reqs, req_ids, req_errs)
        # check request error msg for each unsuccessful requests
        for i in range(num_reqs):
            if strerrno(req_errs[i]) != "NC_NOERR":
                print(f"Error on request {i}:",  strerror(req_errs[i]))
        
         # post 10 requests to write an array of values for the last 10 variables w/o tracking req ids
        for i in range(num_reqs, num_reqs * 2):
            v = f.variables[f'data{i}']
            # post the request to write an array of values
            v.iput_var(datam, start = starts, count = counts)
        
        # all processes commit all pending requests to the file at once using wait_all (collective i/o)
        f.wait_all(num = pncpy.NC_PUT_REQ_ALL)
        f.close()
        assert validate_nc_file(self.file_path) == 0
    
    def tearDown(self):
        # remove the temporary files
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def test_cdf5(self):
        """testing variable iput vara for CDF-5 file format"""

        f = pncpy.File(self.file_path, 'r')
        # test iput_vara and collective i/o wait_all
        for i in range(num_reqs * 2):
            v = f.variables[f'data{i}']
            assert_array_equal(v[:], datares1)

    def test_cdf2(self):
        """testing variable iput vara all for CDF-2 file format"""

        f = pncpy.File(self.file_path, 'r')
        # test iput_vara and collective i/o wait_all
        for i in range(num_reqs * 2):
            v = f.variables[f'data{i}']
            assert_array_equal(v[:], datares1)

    def test_cdf1(self):
        """testing variable iput vara all for CDF-1 file format"""

        f = pncpy.File(self.file_path, 'r')
        # test iput_vara and collective i/o wait_all
        for i in range(num_reqs * 2):
            v = f.variables[f'data{i}']
            assert_array_equal(v[:], datares1)

if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])