# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   The program runs in blocking mode and writes a mapped array section of values into
   a netCDF variables of an opened netCDF file using iput_var method of `Variable` object.
   The library will internally invoke ncmpi_put_varm in C.
"""
import pncpy
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file
import argparse

seed(0)
file_formats = ['64BIT_DATA', '64BIT_OFFSET', None]
file_name = "tst_var_put_varm.nc"


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

xdim=6; ydim=4
# Initial numpy array data to be written to nc variable 
data = np.zeros((xdim,ydim)).astype('f4')
# Internal numpy array data to be written to nc variable using put_varm
datam = randint(0,10,size=(2,3)).astype('f4')
# Reference numpy array for testing 
dataref = data.copy()
dataref[::2, ::2] = datam.transpose()
starts = np.array([0,0])
counts = np.array([3,2])
strides = np.array([2,2])
imap = np.array([1,3]) #would be [2, 1] if not transposing



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

        v1 = f.def_var('data1', pncpy.NC_FLOAT, ('x','y'))
        v2 = f.def_var('data2', pncpy.NC_FLOAT, ('x','y'))

        # initialize variable values
        f.enddef()
        v1[:] = data
        v2[:] = data
        f.close()

        # All processes write subarray to variable with put_var_all (collective i/o)
        f = pncpy.File(filename=self.file_path, mode = 'r+', format=self._file_format, comm=comm, info=None)
        v1 = f.variables['data1']
        v1.put_var_all(datam, start = starts, count = counts, stride = strides, imap = imap)
        # Equivalent to the above method call: v1[::2, ::2] = datam.transpose()

        # Write subarray to variable with put_var (independent i/o)
        v2 = f.variables['data2']
        f.begin_indep()
        if rank < 2:
            v2.put_var(datam, start = starts, count = counts, stride = strides, imap = imap)
            
        f.end_indep()
        f.close()
        comm.Barrier()
        assert validate_nc_file(self.file_path) == 0

    def tearDown(self):
        # Remove the temporary files
        comm.Barrier()
        if (rank == 0) and (self.file_path == file_name):
            os.remove(self.file_path)

    def runTest(self):
        """testing variable put varm all"""

        f = pncpy.File(self.file_path, 'r')
        # test collective i/o put_var
        v1 = f.variables['data1']
        assert_array_equal(v1[:], dataref)
        # test independent i/o put_var
        v2 = f.variables['data2']
        assert_array_equal(v2[:], dataref)
        f.close()


if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
