# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   The program runs in non-blocking mode and makes a request to read an array of values 
   from a netCDF variable of an opened netCDF file using iget_var method of `Variable` class. The 
   library will internally invoke ncmpi_iget_vara in C. 
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
file_name = "tst_var_iget_vara.nc"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
xdim=9; ydim=10; zdim=size*10
# initial values for netCDF variable
data = randint(0,10, size=(xdim,ydim,zdim)).astype('i4')
# generate reference arrayes for testing
dataref = []
for i in range(size):
    dataref.append(data[3:4,:5,i*10:(i+1)*10])
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
        f.close()
        comm.Barrier()
        assert validate_nc_file(self.file_path) == 0


        f = pncpy.File(self.file_path, 'r')
        # each process post 10 requests to read an array of values
        req_ids = []
        v_datas.clear()
        starts = np.array([3, 0, 10 * rank])
        counts = np.array([1, 5, 10])
        for i in range(num_reqs):
            v = f.variables[f'data{i}']
            buff = np.empty(shape = counts, dtype = v.datatype)
            # post the request to read one part of the variable
            req_id = v.iget_var(buff, start = starts, count = counts)
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
            buff = np.empty(shape = counts, dtype = v.datatype)
            # post the request to read an array of values
            v.iget_var(buff, start = starts, count = counts)
            # store the reference of variable values
            v_datas.append(buff)
        
        # commit all pending get requests to the file at once using wait_all (collective i/o)
        req_errs = f.wait_all(num = pncpy.NC_GET_REQ_ALL)
        f.close()
        assert validate_nc_file(self.file_path) == 0
    
    def tearDown(self):
        # remove the temporary files
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def runTest(self):
        """testing variable iget_vara method for CDF-5/CDF-2/CDF-1 file format"""
        # test iget_vara and collective i/o wait_all
        for i in range(num_reqs * 2):
            assert_array_equal(v_datas[i], dataref[rank])

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
