#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   The program defines some variables and dimensions and then rename them using the
   method `renameVariable/dim` of a `Dataset` instance.

    To run the test, execute the following
    `mpiexec -n [num_process] python3 tst_rename.py [test_file_output_dir](optional)`
"""
import pnetcdf
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file
import io

seed(0)
# Format of the data file we will create (64BIT_DATA for CDF-5 and 64BIT_OFFSET for CDF-2 and None for CDF-1)
file_formats = ['NC_64BIT_DATA', 'NC_64BIT_OFFSET', None]
# Name of the test data file
file_name = "tst_rename.nc"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

xdim=9; ydim=10; zdim=11



class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        self._file_format = file_formats.pop(0)
        # Create the test data file
        f = pnetcdf.Dataset(filename=self.file_path, mode = 'w', format=self._file_format, comm=comm, info=None)
        # Define dimensions needed
        f.createDimension('x',xdim)
        f.createDimension('y',ydim)
        f.createDimension('z',zdim)
        # Define 3 variables with same nc datatype NC_INT
        v1 = f.createVariable('data1', pnetcdf.NC_INT, ('x','y','z'))
        v2 = f.createVariable('data2', pnetcdf.NC_INT, ('x','y','z'))
        v3 = f.createVariable('data3', pnetcdf.NC_INT, ('x','y','z'))

        # Rename two dimensions
        f.renameDimension('x', 'new_x')
        f.renameDimension('z', 'new_z')

        # Rename two variables
        f.renameVariable('data1', 'new_data1')
        f.renameVariable('data2', 'new_data2')
        f.close()
        # Validate the created data file using ncvalidator tool
        comm.Barrier()
        assert validate_nc_file(os.environ.get('PNETCDF_DIR'), self.file_path) == 0 if os.environ.get('PNETCDF_DIR') is not None else True



    def tearDown(self):
        # Wait for all processes to finish testing (in multiprocessing mode)
        comm.Barrier()
        # Remove testing file
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def runTest(self):
        """testing writing data of mismatched datatypes with CDF5/CDF2/CDF1 file format"""
        f = pnetcdf.Dataset(self.file_path, 'r')
        # Check variable names and dimension names
        self.assertTrue('new_data1' in f.variables.keys())
        self.assertTrue('new_data2' in f.variables.keys())

        self.assertTrue('new_x' in f.dimensions.keys())
        self.assertTrue('new_z' in f.dimensions.keys())

        v3 = f.variables['data3']

        self.assertTrue('new_z' in v3.dimensions)
        self.assertTrue('new_x' in v3.dimensions)
        self.assertFalse('x' in v3.dimensions)

        f.close()


# Unittest execution order: setUp -> test_method -> tearDown and repeat for each test method
if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    output = io.StringIO()
    runner = unittest.TextTestRunner(stream=output)
    result = runner.run(suite)
    if not result.wasSuccessful():
        print(output.getvalue())
        sys.exit(1)

