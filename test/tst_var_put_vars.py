# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   The program runs in blocking mode and writes an subsampled array of values
   to a variable into a netCDF variable of an opened netCDF file using put_vars method of `Variable` 
   class. The library will internally invoke ncmpi_put_vars in C. 
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
file_name = "tst_var_put_vars.nc"


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
xdim=9; ydim=10; zdim=size*10
# initial values for netCDF variable
data = np.zeros((xdim,ydim,zdim)).astype('i4')
# new array that will be written using iput_var (overwriting some parts of initial values)
datam = randint(0,10, size=(1,3,5)).astype('i4')
# reference array for comparison in the testing phase
datares1, datares2 = data.copy(), data.copy()

for i in range(size):
    datares1[3:4:1,0:6:2,i*10:(i+1)*10:2] = datam

for i in range(min(size,2)):
    datares2[3:4:1,0:6:2,i*10:(i+1)*10:2] = datam

class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        # unit test will iterate through all three file formats
        self._file_format = file_formats.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=self._file_format, comm=comm, info=None)
        f.def_dim('x',xdim)
        f.def_dim('xu',-1)
        f.def_dim('y',ydim)
        f.def_dim('z',zdim)

        v1_u = f.def_var('data1u', pncpy.NC_INT, ('xu','y','z'))
        v2_u = f.def_var('data2u', pncpy.NC_INT, ('xu','y','z'))

        # initialize variable values
        f.enddef()
        v1_u[:] = data
        v2_u[:] = data
        f.close()

        
        f = pncpy.File(filename=self.file_path, mode = 'r+', format=self._file_format, comm=comm, info=None)
        v1_u = f.variables['data1u']
         # equivalent code to the following using indexer syntax: v1_u[3:4,0:6:2,10*rank:10*(rank+1):2] = datam
        starts = np.array([3, 0, 10 * rank])
        counts = np.array([1, 3, 5])
        strides = np.array([1, 2, 2])
        # each process writes a designated subsampled array to variable with put_var_all (collective i/o)
        v1_u.put_var_all(datam, start = starts, count = counts, stride = strides)
        v2_u = f.variables['data2u']
        f.begin_indep()
        if rank < 2:
            # MPI process rank 0 and 1 write a designated subsampled array to variable (independent i/o)
            v2_u.put_var(datam, start = starts, count = counts, stride = strides)
        f.end_indep()
        f.close()
        assert validate_nc_file(self.file_path) == 0

    def tearDown(self):
        # remove the temporary file if test file directory not specified
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def runTest(self):
        """testing variable put vars for CDF-5/CDF-2/CDF-1 file format"""
        f = pncpy.File(self.file_path, 'r')
        # test collective i/o put_var
        v1 = f.variables['data1u']
        # compare returned array with the reference array
        assert_array_equal(v1[:], datares1)
        # test independent i/o put_var
        v2 = f.variables['data2u']
        # compare returned array with the reference array
        assert_array_equal(v2[:], datares2)
        f.close()

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
