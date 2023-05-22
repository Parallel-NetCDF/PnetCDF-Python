# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API. The
   program sets the fill mode and fill values for an individual netCDF record variable using 
   `Variable` class method def_fill() and fill_rec(). This call will change the fill mode 
   which enables filling values for the netCDF variable. The library will internally invoke 
   ncmpi_fill_var_rec in C. 

    To run the test, execute the following
    `mpiexec -n [num_process] python3  tst_var_rec_fill.py [test_file_output_dir](optional)`
"""
import pncpy
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file
import numpy.ma as ma

seed(0)
file_formats = ['64BIT_DATA', '64BIT_OFFSET', None]
file_name = "tst_var_def_fill.nc"
xdim=9; ydim=10 
# file value to be set for each variable
fill_value = np.float32(-1)
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
# define write buffer
datam = np.array([rank, rank]).astype("f4")

# Record variable values expected after writing, assuming 4 processes ("-" means fill values)
#               0.  0.  1.  1.  2.  2.  3.  3.  -  
#               0.  0.  1.  1.  2.  2.  3.  3.  -  
# generate reference data array for testing
dataref = np.empty(shape = (2, 9), dtype = "f4")
dataref.fill(fill_value)
for r in range(size):
    dataref[:, r * 2:(r+1) * 2] = np.array([[r, r], [r, r]])


class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name

        starts = np.array([0, 2 * rank])
        counts = np.array([1, 2])
        # select next file format for testing
        self._file_format = file_formats.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=self._file_format, comm=comm, info=None)
        # define variables and dimensions for testing
        dim_xu = f.def_dim('xu', -1)
        dim_x = f.def_dim('x',xdim)
        # define record variables for testing 
        v1 = f.def_var('data1', pncpy.NC_FLOAT, (dim_xu, dim_x))
        v2 = f.def_var('data2', pncpy.NC_FLOAT, (dim_xu, dim_x))
        # set fill value using _FillValue attribute writes or def_fill
        v1.def_fill(no_fill = 0, fill_value = fill_value)
        v2.put_att("_FillValue", fill_value)

        # enter data mode and write partial values to variables
        f.enddef()
        for v in [v1,v2]:
            starts = np.array([0, 2 * rank])
            counts = np.array([1, 2])
            # fill the 1st record of the record variable
            v.fill_rec(starts[0])
            # write to the 1st record
            v.put_var_all(datam, start = starts, count = counts)
            # fill the 2nd record of the record variable
            starts[0] = 1
            v.fill_rec(starts[0])
            # # write to the 2nd record
            v.put_var_all(datam, start = starts, count = counts)
        f.close() 
        assert validate_nc_file(self.file_path) == 0
    def tearDown(self):
        # remove the temporary files if output test file directory not specified
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)
            pass

    def runTest(self):
        """testing var rec fill for CDF-5/CDF-2/CDF-1 file format"""
        # compare record variable values against reference array
        f = pncpy.File(self.file_path, 'r')
        v1 = f.variables['data1']
        v2 = f.variables['data2']
        assert_array_equal(v1[:], dataref)
        assert_array_equal(v2[:], dataref)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
