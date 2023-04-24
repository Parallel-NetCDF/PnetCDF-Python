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
        # define non-record variables with no fill for testing 
        v1 = f.defineVar('data1', pncpy.NC_FLOAT, ('x','y'))
        v2 = f.defineVar('data2', pncpy.NC_FLOAT, ('x','y'))
        v3 = f.defineVar('data3', pncpy.NC_FLOAT, ('x','y'))
        v4 = f.defineVar('data4', pncpy.NC_FLOAT, ('x','y'))
        # define non-record variables with fill value for testing 
        # v4 = f.defineVar('data4', pncpy.NC_FLOAT, ('x','y'), fill_value = True)
        
        # check current fill node
        for v in [v1, v2, v3, v4]:
            old_no_fill, old_fill_value = v.get_fill_info()
            assert(old_no_fill == 1)
        # set fill value and fill mode for some variables using defineFill
        v1.defineFill(no_fill = 0, fill_value = fill_value)
        v2.defineFill(no_fill = 0)
        v4.defineFill(no_fill = 0)
        # set fill value for some variables using _FillValue attribute writes
        v2.setncattr("_FillValue", fill_value)
        v3._FillValue = fill_value

        # set the variable with fill values back to no fill
        v4.defineFill(no_fill = 1)
        # enter data mode and write partially values to variables
        f.enddef()
        for v in [v1,v2,v3,v4]:
            v.put_var_all(np.float32(rank + 1), index = (rank, rank))

        self.v1_nofill, self.v1_fillvalue = v1.get_fill_info()
        self.v2_nofill, self.v2_fillvalue = v2.get_fill_info()
        self.v3_nofill, self.v3_fillvalue = v3.get_fill_info()
        self.v4_nofill, self.v4_fillvalue = v4.get_fill_info()
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
        # check the fill mode settings of each variable
        # check no_fill flag 
        self.assertTrue(self.v1_nofill == 0)
        self.assertTrue(self.v2_nofill == 0)
        self.assertTrue(self.v3_nofill == 1)
        self.assertTrue(self.v4_nofill == 1)
        # check if fill_value equals the customized fill value
        self.assertTrue(self.v1_fillvalue == fill_value)
        self.assertTrue(self.v2_fillvalue == fill_value)
        self.assertTrue(self.v3_fillvalue == fill_value)

    def test_cdf2(self):
        """testing file set fill mode for CDF-2 file format"""
        # check the fill mode settings of each variable
        # check no_fill flag 
        self.assertTrue(self.v1_nofill == 0)
        self.assertTrue(self.v2_nofill == 0)
        self.assertTrue(self.v3_nofill == 1)
        self.assertTrue(self.v4_nofill == 1)
        # check if fill_value equals the customized fill value
        self.assertTrue(self.v1_fillvalue == fill_value)
        self.assertTrue(self.v2_fillvalue == fill_value)
        self.assertTrue(self.v3_fillvalue == fill_value)

    def test_cdf1(self):
        """testing file set fill mode for CDF-1 file format"""
        # check the fill mode settings of each variable
        # check no_fill flag 
        self.assertTrue(self.v1_nofill == 0)
        self.assertTrue(self.v2_nofill == 0)
        self.assertTrue(self.v3_nofill == 1)
        self.assertTrue(self.v4_nofill == 1)
        # check if fill_value equals the customized fill value
        self.assertTrue(self.v1_fillvalue == fill_value)
        self.assertTrue(self.v2_fillvalue == fill_value)
        self.assertTrue(self.v3_fillvalue == fill_value)



if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])