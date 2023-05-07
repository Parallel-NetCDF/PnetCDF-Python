# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.The 
   program runs in non-blocking mode and makes a request to simultaneously transposes and
    subsample, and read a variable of an opened netCDF file using iget_var method of `Variable` 
    class. The library will internally invoke ncmpi_iget_varm in C. 
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
file_name = "tst_var_iget_varm.nc"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
xdim=6; ydim=4
# numpy array data to be written to nc variable 
data = randint(0,10,size=(xdim,ydim)).astype('f4')
# reference numpy array for testing 
dataref = data[::2, ::2].transpose()
starts = np.array([0,0])
counts = np.array([3,2])
strides = np.array([2,2])
imaps = np.array([1,3]) #would be [2, 1] if not transposing

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
        f.def_dim('x',xdim)
        f.def_dim('y',ydim)

        # define 20 netCDF variables
        for i in range(num_reqs * 2):
            v = f.def_var(f'data{i}', pncpy.NC_FLOAT, ('x','y'))
        # initialize variable values
        f.enddef()
        for i in range(num_reqs * 2):
            v = f.variables[f'data{i}']
            v[:] = data
        f.close()
        assert validate_nc_file(self.file_path) == 0

        f = pncpy.File(self.file_path, 'r')
        # each process post 10 requests to read an subsampled array of values
        req_ids = []
        # reinialize the list of returned data references
        v_datas.clear()
        for i in range(num_reqs):
            v = f.variables[f'data{i}']
            v_data = np.zeros((2,3), dtype = np.float32)
            # post the request to read one part of the variable
            req_id = v.iget_var(v_data, start = starts, count = counts, stride = strides, imap = imaps)
            # track the reqeust ID for each read reqeust 
            req_ids.append(req_id)
            # store the reference of variable values
            v_datas.append(v_data)
        f.end_indep()
        # commit those 10 requests to the file at once using wait_all (collective i/o)
        req_errs = [None] * num_reqs
        f.wait_all(num_reqs, req_ids, req_errs)
        # check request error msg for each unsuccessful requests
        for i in range(num_reqs):
            if strerrno(req_errs[i]) != "NC_NOERR":
                print(f"Error on request {i}:",  strerror(req_errs[i]))
        
         # post 10 requests to read a subsampled array of values for the last 10 variables w/o tracking req ids
        for i in range(num_reqs, num_reqs * 2):
            v = f.variables[f'data{i}']
            v_data = np.zeros((2,3), dtype = np.float32)
            # post the request to read an subsampled array of values
            v.iget_var(v_data, start = starts, count = counts, stride = strides, imap = imaps)
            # store the reference of variable values
            v_datas.append(v_data)
        
        # commit all pending get requests to the file at once using wait_all (collective i/o)
        req_errs = f.wait_all(num = pncpy.NC_GET_REQ_ALL)
        f.close()
        assert validate_nc_file(self.file_path) == 0
    

    def runTest(self):
        """testing variable iget_varm method for CDF-5/CDF-2/CDF-1 file format"""
        # test iget_varm and collective i/o wait_all
        for i in range(num_reqs * 2):
            assert_array_equal(v_datas[i], dataref)

    def tearDown(self):
        # remove the temporary files if test file directory not specified
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
