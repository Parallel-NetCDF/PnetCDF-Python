# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   The program writes the data of a different type than the one that was initially defined 
   for the NC variable. The write uses indexer operators (numpy array style). 

    To run the test, execute the following
    `mpiexec -n [num_process] python3 tst_var_type.py [test_file_output_dir](optional)`
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
file_name = "tst_var_type.nc"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

xdim=9; ydim=10; zdim=11

data = randint(0,10,size=(xdim,ydim,zdim)).astype('i4')
# Numpy array data to be written to nc variable (mismatched datatype with variable type)
datas = data.astype('i2')
dataf = data.astype('f8')
# Numpy array data to be written to nc variable (datatype only supported by CDF-5)
dataull = data.astype('u8')
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
        f.def_dim('y',ydim)
        f.def_dim('z',zdim)
        # Define 3 variables with same nc datatype NC_INT
        v1 = f.def_var('data1', pncpy.NC_INT, ('x','y','z'))
        v2 = f.def_var('data2', pncpy.NC_INT, ('x','y','z'))
        v3 = f.def_var('data3', pncpy.NC_INT, ('x','y','z'))

        # Enter data mode
        f.enddef()
        # Write numpy array of mismatched datatypes to variables (conversion occurs)
        v1[:,::-1,:] = datas
        v2[:,::-1,:] = dataf
        v3[:,::-1,:] = dataull
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
        """testing writing data of mismatched datatypes with CDF5/CDF2/CDF1 file format"""
        f = pncpy.File(self.file_path, 'r+')
        f.end_indep()
        # Compare returned variable data with reference data
        v1 = f.variables['data1']   
        assert_array_equal(v1[:] , dataref)
        v2 = f.variables['data2']
        assert_array_equal(v2[:], dataref)
        v3 = f.variables['data3']
        assert_array_equal(v3[:], dataref)
        if self._file_format != "64BIT_DATA":
            f.redef()
        try:
            f.def_var('data3', pncpy.NC_UINT64, ('x','y','z'))
        except RuntimeError:
            pass
        else:
            raise RuntimeError("This should have raised RuntimeError: Attempting \
                               CDF-5 operation on strict CDF or CDF-2 file")
        f.close()


# Unittest execution order: setUp -> test_method -> tearDown and repeat for each test method
if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

