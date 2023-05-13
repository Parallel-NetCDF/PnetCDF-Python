# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API. The
   program create a number of netCDF files using `File` class constructor and inquiry the info
   about opened files using utils function inq_files_opened. The python library will internally
   invoke ncmpi_inq_files_opened function in C. 

   To run the test, execute the following
    `mpiexec -n [num_process] python3  tst_inq_opened.py [test_file_output_dir](optional)`

"""
import pncpy
from pncpy import set_default_format, inq_default_format, inq_file_format, inq_files_opened
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file

seed(0)

# Name of the test data file
file_names = ["tst_inq_opened_0.nc", "tst_inq_opened_1.nc", "tst_inq_opened_2.nc"]
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
        # create and close all netCDF files
        for file_name in self.file_paths:
            f = pncpy.File(filename=file_name, mode = 'w', comm=comm, info=None)
            f.close() 
            assert validate_nc_file(file_name) == 0
        # inquiry current opened files 
        self.num_opened_checkpoint1= inq_files_opened()
        # reopen some netCDF files with different modes
        f1 = pncpy.File(filename=file_names[0], mode = 'r', comm=comm, info=None)
        f2 = pncpy.File(filename=file_names[1], mode = 'a', comm=comm, info=None)
        # store ncids for testing purpose
        self.ncid1 = f1._ncid
        self.ncid2 = f2._ncid
        # inquiry current opened files and ncids
        self.num_opened_checkpoint2 = inq_files_opened()
        self.ncids_checkpoint2 = [None] * self.num_opened_checkpoint2
        inq_files_opened(self.ncids_checkpoint2)
        f1.close()
        f2.close()

    def runTest(self):
        """testing inquiry opened files """
        f = pncpy.File(self.file_paths[0], 'r')
        self.assertEqual(self.num_opened_checkpoint1, 0)
        self.assertEqual(self.num_opened_checkpoint2, 2)
        self.assertEqual(self.ncids_checkpoint2, [self.ncid1, self.ncid2])



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

