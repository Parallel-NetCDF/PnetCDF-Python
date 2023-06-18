# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   It is a program which simultaneously transposes, subsamples and reads a variable within a netCDF file using 
   get_var method of `Variable` class, the library internally will invoke ncmpi_get_varm in C. 
"""
import pncpy
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file

seed(0)
# Format of the data file we will create (64BIT_DATA for CDF-5 and 64BIT_OFFSET for CDF-2)
file_formats = ['64BIT_DATA', '64BIT_OFFSET', None]
# Name of the test data file
file_name = "tst_var_get_varm.nc"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

xdim=6; ydim=4
# Numpy array data to be written to nc variable 
data = randint(0,10,size=(xdim,ydim)).astype('f4')
# Reference numpy array for testing 
dataref = data[::2, ::2].transpose()
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
        # Create the test data file 
        f = pncpy.File(filename=self.file_path, mode = 'w', format=self._file_format, comm=comm, info=None)
        # Define dimensions needed, one of the dims is unlimited
        f.def_dim('x',xdim)
        f.def_dim('y',ydim)

        # For the variable dimensioned with limited dims, we are writing 2D data on a 4 X 6 grid 
        v1 = f.def_var('data1', pncpy.NC_FLOAT, ('x','y'))

        # Enter data mode
        f.enddef()
        # Write to variables using indexer 
        v1[:] = data
        f.close()
        # Validate the created data file using ncvalidator tool
        assert validate_nc_file(self.file_path) == 0

    def tearDown(self):
        # Wait for all processes to finish testing (in multiprocessing mode)
        comm.Barrier()
        # Remove testing file
        if (rank == 0) and (self.file_path == file_name):
            os.remove(self.file_path)

    def runTest(self):
        """testing reading variables with CDF5/CDF2/CDF1 file format"""
        f = pncpy.File(self.file_path, 'r')
       
        f.end_indep()
        v1 = f.variables['data1']
        v1_data = np.empty((2,3), dtype = np.float32)
        v1.get_var_all(buff = v1_data, start = starts, count = counts, stride = strides, imap = imap)
        assert_array_equal(v1_data, dataref)

         # Test reading from the variable in independent mode
        f.begin_indep()
        v1_data = np.empty((2,3), dtype = np.float32)
        v1.get_var(buff = v1_data, start = starts, count = counts, stride = strides, imap = imap)
        assert_array_equal(v1_data, dataref)
        f.close()

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
