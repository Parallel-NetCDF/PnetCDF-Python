# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   The program runs read a single element from a netCDF variable of an opened netCDF file 
   using get_var method of `Variable` class. The library will internally invoke ncmpi_get_var1 in C. 
"""
import pncpy
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file

seed(0)
file_formats = ['64BIT_DATA', '64BIT_OFFSET', None]
file_name = "tst_var_get_var1.nc"
xdim=9; ydim=10; zdim=11
# initial values for netCDF variable
data = randint(0,10, size=(xdim,ydim,zdim)).astype('i4')
# generate reference numpy arrays for testing
datarev = data[:,::-1,:].copy()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()



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

        v1_u = f.def_var('data1u', pncpy.NC_INT, ('xu','y','z'))

        #initialize variable values
        f.enddef()
        v1_u[:,::-1,:] = data
        f.close()
        assert validate_nc_file(self.file_path) == 0

    def runTest(self):
        """testing variable get vara for CDF-5/CDF-2/CDF-1 file format"""
        f = pncpy.File(self.file_path, 'r')
        v1 = f.variables['data1u']
        # test collective i/o put var1
         # equivalent code to the following using indexer syntax: value = v1[rank][rank][rank] 
        index = (rank, rank, rank)
        f.begin_indep()
        # all processes read the designated cell of the variable using independent i/o
        buff = np.empty((), v1.dtype)
        v1.get_var(buff, index = index)
        # compare returned value against reference value
        assert_equal(buff, datarev[rank][rank][rank])
        # test independent i/o put var1
        f.end_indep()
        # all processes read the designated cell of the variable using collective i/o
        buff = np.empty((), v1.dtype)
        v1.get_var_all(buff, index = index)
        # compare returned value against reference value
        assert_equal(buff, datarev[rank][rank][rank])
        f.close()

    def tearDown(self):
        # remove the temporary files if test file directory is not specified
        comm.Barrier()
        if (rank == 0) and (self.file_path == file_name):
            os.remove(self.file_path)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

