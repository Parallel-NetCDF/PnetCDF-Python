# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   The program runs write the whole value into a netCDF variable of an opened netCDF file using 
   put_var method of `Variable` class. The library will internally invoke ncmpi_put_var in C. 
"""
import pncpy
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal,\
assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file

seed(0)
data_models = ['64BIT_DATA', '64BIT_OFFSET', None]
file_name = "tst_var_put_var.nc"
xdim=9; ydim=10; zdim=11 
# generate numpy array to write to the whole netCDF variable
data = randint(0,10, size=(xdim,ydim,zdim)).astype('i4')
datarev = data[:,::-1,:].copy()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()



class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        data_model = data_models.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=data_model, Comm=comm, Info=None)
        # define variables and dimensions for testing
        f.defineDim('x',xdim)
        f.defineDim('xu',-1)
        f.defineDim('y',ydim)
        f.defineDim('z',zdim)

        v1 = f.defineVar('data1', pncpy.NC_INT, ('x','y','z'))
        v2 = f.defineVar('data2', pncpy.NC_INT, ('x','y','z'))

        # all MPI processes writes the whole variable with the same value (collective i/o)
        f.enddef()
        v1 = f.variables['data1']
        v1.put_var_all(data)

        # MPI process rank 0 writes the whole variable (independent i/o)
        f.begin_indep()
        v2 = f.variables['data2']
        if rank == 0:
            v2.put_var(datarev)
        f.end_indep()
        f.close()
        comm.Barrier()
        assert validate_nc_file(self.file_path) == 0
    
    def tearDown(self):
        # remove the temporary files
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)
            pass

    def test_cdf5(self):
        """testing variable put var all"""

        f = pncpy.File(self.file_path, 'r')
        # test collective i/o put_var1
        v1 = f.variables['data1']
        assert_array_equal(v1[:], data)
        # test independent i/o put_var1
        v2 = f.variables['data2']
        assert_array_equal(v2[:], datarev)
        f.close()

    def test_cdf2(self):
        """testing variable put var all"""
        f = pncpy.File(self.file_path, 'r')
        # test collective i/o put_var1
        f.enddef()
        v1 = f.variables['data1']
        assert_array_equal(v1[:], data)
        # test independent i/o put_var1
        v2 = f.variables['data2']
        assert_array_equal(v2[:], datarev)
        f.close()

    def test_cdf1(self):
        """testing variable put var all"""
        f = pncpy.File(self.file_path, 'r')
        # test collective i/o put_var1
        f.enddef()
        v1 = f.variables['data1']
        assert_array_equal(v1[:], data)
        # test independent i/o put_var1
        v2 = f.variables['data2']
        assert_array_equal(v2[:], datarev)
        f.close()



if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])