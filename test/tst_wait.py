# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   The program runs in non-blocking mode and makes some requests to write to a variable 
   into a netCDF variable and commit them using wait/wait_all method of `File` class. The 
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
# file format selections: CDF-5(64BIT_DATA'), CDF-2('64BIT_OFFSET') and CDF-1 (None)
file_formats = ['64BIT_DATA', '64BIT_OFFSET', None]
file_name = "tst_wait.nc"

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
# initialize the list to store request ids 
req_ids_tst1 = []
req_ids_tst2 = []
bad_req_ids = list(range(num_reqs))
# initialize the list to store buff references from iget requests
v_data = []

class FileTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        # select the next file format for testing
        self._file_format = file_formats.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=self._file_format, comm=comm, info=None)
        # f.def_dim('x',xdim)
        f.def_dim('xu',-1)
        f.def_dim('y',ydim)
        f.def_dim('z',zdim)

        # define 20 netCDF variables: 10 for testing wait_all(), 10 for testing wait()
        for i in range(3 * num_reqs):
            v = f.def_var(f'data{i}', pncpy.NC_INT, ('xu','y','z'))
        # initialize variable values
        f.enddef()
        for i in range(3 * num_reqs):
            v = f.variables[f'data{i}']
            v[:] = data

        # each process post 10 iput requests to write an array of values to the first 10 variables
        starts = np.array([3, 0, 10 * rank])
        counts = np.array([1, 5, 10])
        # reinialize the request id list
        req_ids_tst1.clear()
        for i in range(num_reqs):
            v = f.variables[f'data{i}']
            # post the request to write an array of values
            req_id = v.iput_var(datam, start = starts, count = counts)
            # track the reqeust ID for each write reqeust 
            req_ids_tst1.append(req_id) if i < 10 else req_ids_tst2.append(req_id)
        # TEST 1 - wait_all (collective i/o)
        # check number of pending requests
        assert(f.inq_nreqs() == num_reqs)
        f.end_indep()
        # all processes commit the first 10 requests to the file at once using wait_all (collective i/o)
        req_errs = [None] * num_reqs
        f.wait_all(num_reqs, req_ids_tst1, req_errs)
        # check request error msg for each unsuccessful requests
        for i in range(num_reqs):
            if strerrno(req_errs[i]) != "NC_NOERR":
                print(f"Error on request {i}:",  strerror(req_errs[i]))
        # check if all requests are committed
        assert(f.inq_nreqs() == 0)

        # TEST 2 - wait (independent i/o)
        req_ids_tst2.clear()
         # post 10 requests to write an array of values for the last 10 variables
        for i in range(num_reqs, num_reqs * 2):
            v = f.variables[f'data{i}']
            # post the request to write an array of values
            req_id = v.iput_var(datam, start = starts, count = counts)
            # track the reqeust ID for each write reqeust 
            req_ids_tst2.append(req_id)
        # check number of pending requests
        assert(f.inq_nreqs() == num_reqs)
        f.begin_indep()
        # each process commits the rest 10 requests to the file at once using wait (independent i/o)
        req_errs = [None] * num_reqs
        f.wait(10, req_ids_tst2, req_errs)
        # check request error msg for each unsuccessful requests
        for i in range(num_reqs):
            if strerrno(req_errs[i]) != "NC_NOERR":
                print(f"Error on request {i}:",  strerror(req_errs[i]))
        # check if all requests are committed
        assert(f.inq_nreqs() == 0)

        # TEST 3 - wait on invalid req ids
        req_errs = [None] * num_reqs
        try: 
            # try commit all requests without terminating the program
            f.wait(num_reqs, bad_req_ids, req_errs)
        except RuntimeError:
            pass
        else:
            raise RuntimeError("This should have failed.")
        finally:
            # check request error msg for each unsuccessful requests
            for i in range(num_reqs):
                assert(strerrno(req_errs[i]) == "NC_EINVAL_REQUEST")
        f.close()
        assert validate_nc_file(self.file_path) == 0

    def runTest(self):
        """testing File wait method for CDF-5/CDF-2/CDF-1 file format"""

        f = pncpy.File(self.file_path, 'r')
        # test collective i/o wait_all & independent i/o wait
        for i in range(2 * num_reqs):
            v = f.variables[f'data{i}']
            # compare stored array with reference array
            assert_array_equal(v[:], datares1)
            # check request ids - successful ids should be replaced with NC_REQ_NULL
            if i < 10:
                self.assertTrue(req_ids_tst1[i] == pncpy.NC_REQ_NULL)
            else:
                self.assertTrue(req_ids_tst2[i - 10] == pncpy.NC_REQ_NULL)
        # test invalid request ids
        # invalid request id list should remain unchanged
        assert_array_equal(bad_req_ids, list(range(num_reqs)))

    def tearDown(self):
        # remove the temporary files if test file output directory not specified
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(FileTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
