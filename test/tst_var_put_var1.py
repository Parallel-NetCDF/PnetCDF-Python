# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   The program runs in blocking mode and writes a single element to a variable 
   into a netCDF variable of an opened netCDF file using put_var method of `Variable` class. The 
   library will internally invoke ncmpi_put_var1 in C. 
"""
import pncpy
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file

seed(0)
# file format selections: CDF-5(64BIT_DATA'), CDF-2('64BIT_OFFSET') and CDF-1 (None)
file_formats = ['64BIT_DATA', '64BIT_OFFSET', None]
file_name = "tst_var_put_var1.nc"
xdim=9; ydim=10; zdim=11
# initial values for netCDF variable
data = randint(0,10, size=(xdim,ydim,zdim)).astype('i4')
datarev = data[:,::-1,:].copy()
# reference array for comparison in the testing phase
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
for i in range(size):
    datarev[i][i][i] = i * 10 + 1


class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        # select the next file format for testing
        self._file_format = file_formats.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=self._file_format, comm=comm, info=None)
        f.def_dim('x',xdim)
        f.def_dim('xu',-1)
        f.def_dim('y',ydim)
        f.def_dim('z',zdim)

        v1_u = f.def_var('data1u', pncpy.NC_INT, ('xu','y','z'))
        v2_u = f.def_var('data2u', pncpy.NC_INT, ('xu','y','z'))

        #initialize variable values
        f.enddef()
        v1_u[:,::-1,:] = data
        v2_u[:,::-1,:] = data
        f.close()

        
        f = pncpy.File(filename=self.file_path, mode = 'r+', format=self._file_format, comm=comm, info=None)
        v1_u = f.variables['data1u']
        # equivalent code to the following using indexer syntax: v1_u[rank][rank][rank] = value
        index = (rank, rank, rank)
        value = np.int32(rank * 10 + 1)
        # each process change a designated element of the variable with collective i/o
        v1_u.put_var_all(value, index)
        
        f.begin_indep()
        v1_u = f.variables['data2u']
        # each process change a designated element of the variable with independent i/o
        v2_u.put_var(value, index)
        f.end_indep()

        f.close()
        assert validate_nc_file(self.file_path) == 0
    
    def tearDown(self):
        # remove the temporary file if test file directory not specified
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def runTest(self):
        """testing variable put var1 for CDF-5/CDF-2/CDF-1 file format"""

        f = pncpy.File(self.file_path, 'r')
        # test collective i/o put var1
        v1 = f.variables['data1u']
        # compare returned array with the reference array
        assert_array_equal(v1[:], datarev)
        # test independent i/o put var1
        v2 = f.variables['data2u']
        assert_array_equal(v2[:], datarev)
        f.close()


if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
