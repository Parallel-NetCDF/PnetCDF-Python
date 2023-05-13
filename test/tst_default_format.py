# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This test program is intended to illustrate the use of the pnetCDF python API.
   The program sets the default file format by using set_default_format function and 
    then create a number of netCDF files with default format for testing. Internally,
   the library will invoke ncmpi_set_default_format and ncmpi_create in C.

   To run the test, execute the following
    `mpiexec -n [num_process] python3  tst_default_format.py [test_file_output_dir](optional)`

"""
import pncpy
from pncpy import set_default_format, inq_default_format, inq_file_format
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file

seed(0)

# Name of the test data file
file_names = ["tst_default_format_0.nc", "tst_default_format_1.nc", "tst_default_format_2.nc"]
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()




class FileTestCase(unittest.TestCase):

    def setUp(self):
        self.file_paths = []
        for file_name in file_names:
            if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
                file_path = os.path.join(sys.argv[1], file_name)
            else:
                file_path = file_name
            self.file_paths.append(file_path)
        # change default file format to "64BIT_DATA"
        old_format = set_default_format(pncpy.NC_FORMAT_64BIT_DATA)
        assert(old_format == pncpy.NC_FORMAT_CLASSIC)
        # create CDF-5 netCDF files using current default format
        f = pncpy.File(filename=self.file_paths[0], mode = 'w', comm=comm, info=None)
        f.close() 
        assert validate_nc_file(self.file_paths[0]) == 0
        # inquiry current default (for testing)
        self.new_default = inq_default_format()
        # create CDF-2 netCDF files by overwriting default
        f = pncpy.File(filename=self.file_paths[1], mode = 'w', format = "64BIT_OFFSET", comm=comm, info=None)
        f.close() 
        assert validate_nc_file(self.file_paths[1]) == 0
        # change default file format back to "CLASSIC"
        old_format = set_default_format(pncpy.NC_FORMAT_CLASSIC)
        assert(old_format == pncpy.NC_FORMAT_64BIT_DATA)
        # create CDF-1 netCDF files using default
        f = pncpy.File(filename=self.file_paths[2], mode = 'w', comm=comm, info=None)
        f.close() 
        assert validate_nc_file(self.file_paths[2]) == 0


    def runTest(self):
        """testing set default format for file formats"""
        f = pncpy.File(self.file_paths[0], 'r')
        self.assertTrue(f.file_format == "64BIT_DATA" or f.file_format == "CDF5")
        f.close()
        f = pncpy.File(self.file_paths[1], 'r')
        self.assertTrue(f.file_format == "64BIT_OFFSET" or f.file_format == "64BIT" or f.file_format == "CDF2")
        f.close()
        f = pncpy.File(self.file_paths[2], 'r')
        self.assertTrue(f.file_format == "CLASSIC")
        f.close()
        self.assertTrue(inq_file_format(self.file_paths[0]) == pncpy.NC_FORMAT_64BIT_DATA)
        self.assertTrue(inq_file_format(self.file_paths[1]) == pncpy.NC_FORMAT_64BIT_OFFSET)
        self.assertTrue(inq_file_format(self.file_paths[2]) == pncpy.NC_FORMAT_CLASSIC)


    def tearDown(self):
        # Wait for all processes to finish testing (in multiprocessing mode)
        comm.Barrier()
        # Remove testing file if output test file directory not specified
        for file_path in self.file_paths:
            if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
                os.remove(file_path)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(FileTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

