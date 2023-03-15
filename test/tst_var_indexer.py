# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   It is a program which writes and reads variables to netCDF file using indexer operators 
   (numpy array style). When writing with indexer syntax, the library internally will invoke 
   put_vara/vars. Similarly when reading with indexer syntax the library internally will  
   invoke get_vara/vars
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
data_models = ['64BIT_DATA', '64BIT_OFFSET', None]
# Name of the test data file
file_name = "tst_var_indexer.nc"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

xdim=9; ydim=10; zdim=11
# Numpy array data to be written to nc variable 
data = randint(0,10,size=(xdim,ydim,zdim)).astype('i4')
# Reference numpy array for testing 
dataref = data[:,::-1,:].copy()



class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        data_model = data_models.pop(0)
        # Create the test data file 
        f = pncpy.File(filename=self.file_path, mode = 'w', format=data_model, Comm=comm, Info=None)
        # Define dimensions needed, one of the dims is unlimited
        f.defineDim('x',xdim)
        f.defineDim('xu',-1)
        f.defineDim('y',ydim)
        f.defineDim('z',zdim)
        # For the variable dimensioned with limited dims, we are writing 3D data on a 9 x 10 x 11 grid 
        v1 = f.defineVar('data1', pncpy.NC_INT, ('x','y','z'))
        # For the record variable, we are writing 3D data on unlimited x 10 x 11 grid
        v1_u = f.defineVar('data1u', pncpy.NC_INT, ('xu','y','z'))
        # Define another set of variables for indepedent mode testing
        v2 = f.defineVar('data2', pncpy.NC_INT, ('x','y','z'))
        v2_u = f.defineVar('data2u', pncpy.NC_INT, ('xu','y','z'))

        # Enter data mode
        f.enddef()
        # Write to variables using indexer in collective mode ()
        v1[:,::-1,:] = data
        v1_u[:,::-1,:] = data

        # Enter independent data mode
        f.begin_indep()
        # Write to variables using indexer in indepedent mode

        v2[:,::-1,:] = data
        v2_u[:,::-1,:] = data
        f.end_indep()
        f.close()
        # Validate the created data file using ncvalidator tool
        comm.Barrier()
        assert validate_nc_file(self.file_path) == 0
        

    def tearDown(self):
        # Wait for all processes to finish testing (in multiprocessing mode)
        comm.Barrier()
        # Remove testing file
        if (rank == 0) and (self.file_path == file_name):
            os.remove(self.file_path)

    def test_cdf5(self):
        """testing writing and reading variables in CDF5 data file"""
        f = pncpy.File(self.file_path, 'r')
        f.end_indep()
        v1 = f.variables['data1']
        # Test the variable previously written in collective mode
        # Compare returned variable data with reference data
        assert_array_equal(v1[:] , dataref)
        v1_u = f.variables['data1u']
        assert_array_equal(v1_u[:], dataref)
        # Run same tests for the variable written in independent mode

        v2 = f.variables['data2']
        assert_array_equal(v2[:], dataref)

        v2_u = f.variables['data2u']
        assert_array_equal(v2_u[:], dataref)
        f.close()

    def test_cdf2(self):
        """testing writing and reading variables in CDF2 data file"""

        f = pncpy.File(self.file_path, 'r')
        v = f.variables['data1']
        # Test the variable previously written in collective mode
        # Compare returned variable data with reference data
        assert_array_equal(v[:], dataref)
        v1_u = f.variables['data1u']
        assert_array_equal(v1_u[:], dataref)
        # Run same tests for the variable written in independent mode
        v2 = f.variables['data2']
        assert_array_equal(v2[:], dataref)

        v2_u = f.variables['data2u']
        assert_array_equal(v2_u[:], dataref)
        f.close()

    def test_cdf1(self):
        """testing writing and reading variables in CDF2 data file"""

        f = pncpy.File(self.file_path, 'r')
        v = f.variables['data1']
        # Test the variable previously written in collective mode
        # Compare returned variable data with reference data
        assert_array_equal(v[:], dataref)
        v1_u = f.variables['data1u']
        assert_array_equal(v1_u[:], dataref)
        # Run same tests for the variable written in independent mode
        v2 = f.variables['data2']
        assert_array_equal(v2[:], dataref)

        v2_u = f.variables['data2u']
        assert_array_equal(v2_u[:], dataref)
        f.close()


# Unittest execution order: setUp -> test_cdf5 -> tearDown -> setUp -> test_cdf2 -> tearDown
if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])
