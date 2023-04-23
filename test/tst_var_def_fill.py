# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API. The
   program sets the fill mode for an individual netCDF variable using `Variable` class
   method defineFill(). This call will change the fill mode for all non-record variables 
   defined so far and change the default fill mode for new non-record variables defined following
   this call. The library will internally invoke ncmpi_set_fill in C. 
"""
import pncpy
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file

seed(0)
data_models = ['64BIT_DATA', '64BIT_OFFSET', None]
file_name = "tst_var_def_fill.nc"
xdim=9; ydim=10 
# file value to be set for each variable
fill_value = np.float32(-1)
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()



class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        # select next file format for testing
        data_model = data_models.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=data_model, Comm=comm, Info=None)
        # define variables and dimensions for testing
        f.defineDim('x',xdim)
        f.defineDim('xu', -1)
        f.defineDim('y',ydim)
        # define non-record variables for testing
        v1 = f.defineVar('data1', pncpy.NC_FLOAT, ('x','y'))
        v2 = f.defineVar('data2', pncpy.NC_FLOAT, ('x','y'))
        v3 = f.defineVar('data3', pncpy.NC_FLOAT, ('xu','y'))
        v4 = f.defineVar('data4', pncpy.NC_FLOAT, ('xu','y'))
        # verify current fill node is no_fill
        for v in [v1, v2, v3, v4]:
            old_no_fill, old_fill_value = v.get_fill_info()
            assert(old_no_fill == 1)
        # set fill value for some variables using defineFill
        v1.defineFill(no_fill = 0, fill_value = fill_value)
        v3.defineFill(no_fill = 0, fill_value = fill_value)
        # set fill value for some variables using _FillValue attribute writes
        v2.setncattr('_FillValue', fill_value)
        v4.setncattr('_FillValue', fill_value)

        # enter data mode and write partially values to the non-record variables
        f.enddef()
        for v in [v1,v2]:
            v.put_var_all(np.float32(rank + 1), index = (rank, rank))
        f.close()
        assert validate_nc_file(self.file_path) == 0
    
    def tearDown(self):
        # remove the temporary files
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)
            pass

    def test_cdf5(self):
        """testing file set fill mode for CDF-5 file format"""
        f = pncpy.File(self.file_path, 'r')
        for i in range(1,4):
            v = f.variables[f'data{i}']
            # check the fill mode settings of each variable
            no_fill, cur_fill_value = v.get_fill_info()
            # check if no_fill flag is set to 0 
            self.assertTrue(no_fill == 0)
            # check if fill_value equals default fill value
            self.assertTrue(cur_fill_value == fill_value)
        f.close()

    def test_cdf2(self):
        """testing file set fill mode for CDF-2 file format"""
        f = pncpy.File(self.file_path, 'r')
        for i in range(1,4):
            v = f.variables[f'data{i}']
            # check the fill mode settings of each variable
            no_fill, cur_fill_value = v.get_fill_info()
            # check if no_fill flag is set to 0 
            self.assertTrue(no_fill == 0)
            # check if fill_value equals default fill value
            self.assertTrue(cur_fill_value == fill_value)
        f.close()

    def test_cdf1(self):
        """testing file set fill mode for CDF-1 file format"""
        f = pncpy.File(self.file_path, 'r')
        for i in range(1,4):
            v = f.variables[f'data{i}']
            # check the fill mode settings of each variable
            no_fill, cur_fill_value = v.get_fill_info()
            # check if no_fill flag is set to 0 
            self.assertTrue(no_fill == 0)
            # check if fill_value equals default fill value
            self.assertTrue(cur_fill_value == fill_value)
        f.close()



if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])