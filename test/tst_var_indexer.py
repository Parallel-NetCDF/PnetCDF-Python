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
   ncmpi_put_vara/vars. Similarly when reading with indexer syntax the library internally will
   invoke ncmpi_get_vara/vars

   To run the test, execute the following
    `mpiexec -n [num_process] python3 tst_var_indexer.py [test_file_output_dir](optional)`

"""
import pncpy
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file

seed(0)
# Format of the data file we will create (64BIT_DATA for CDF-5 and 64BIT_OFFSET for CDF-2 and None for CDF-1)
file_formats = ['64BIT_DATA', '64BIT_OFFSET', None]
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
        self._file_format = file_formats.pop(0)
        # Create the test data file 
        f = pncpy.File(filename=self.file_path, mode = 'w', format=self._file_format, comm=comm, info=None)
        # Define dimensions needed, one of the dims is unlimited
        f.def_dim('x',xdim)
        f.def_dim('xu',-1)
        f.def_dim('y',ydim)
        f.def_dim('z',zdim)
        # For the variable dimensioned with limited dims, we are writing 3D data on a 9 x 10 x 11 grid 
        v1 = f.def_var('data1', pncpy.NC_INT, ('x','y','z'))
        # For the record variable, we are writing 3D data on unlimited x 10 x 11 grid
        v1_u = f.def_var('data1u', pncpy.NC_INT, ('xu','y','z'))
        # Define another set of variables for indepedent mode testing
        v2 = f.def_var('data2', pncpy.NC_INT, ('x','y','z'))
        v2_u = f.def_var('data2u', pncpy.NC_INT, ('xu','y','z'))

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
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def runTest(self):
        """testing writing and reading variables with CDF5/CDF2/CDF1 file format"""
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


if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

