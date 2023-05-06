# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API. The
   program write a number of attributes and variables to a netCDF file using `File` class
   methods. Then the program will inquiry the file info in terms of the defined dimensions, 
   variables, attributes, file formats, etc. The python library will internally invoke 
   ncmpi_inq Family functions in C. 

   To run the test, execute the following
    `mpiexec -n [num_process] python3  tst_file_inq.py [test_file_output_dir](optional)`

"""
import pncpy
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file

seed(0)
file_formats = ['64BIT_DATA', '64BIT_OFFSET', None]
file_name = "tst_file_inq.nc"
xdim=9; ydim=10; zdim = 11

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
        file_format = file_formats.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=file_format, Comm=comm, Info=None)
        # write global attributes for testing
        f.attr1 = 'one'
        f.putncatt('attr2','two')
        # define variables and dimensions for testing
        dim_xu = f.def_dim('xu',-1)
        dim_x = f.def_dim('x',xdim)
        dim_y = f.def_dim('y',ydim)
        dim_z = f.def_dim('z',zdim)

        v1_u = f.def_var('data1u', pncpy.NC_INT, (dim_xu, dim_y, dim_z))
        v2_u = f.def_var('data2u', pncpy.NC_INT, (dim_xu, dim_y, dim_z))
        v1 = f.def_var('data1', pncpy.NC_INT, (dim_x, dim_y, dim_z))
        v2 = f.def_var('data2', pncpy.NC_INT, (dim_x, dim_y, dim_z))

        
        f.close()
        assert validate_nc_file(self.file_path) == 0

        
        # reopen the netCDF file in read-only mode
        f = pncpy.File(filename=self.file_path, mode = 'r')
        # inquiry and store the number of vars 
        self.nvars = len(f.variables)
        # inquiry and store the number of dims 
        self.ndims = len(f.dimensions)
        # inquiry and store the number of global attributes
        self.nattrs = len(f.ncattrs())
        # inquiry the unlimited dim instance and store its name
        unlimited_dim = f.inq_unlimdim()
        self.unlimited_dim_name = unlimited_dim.name
        # inquiry and store the file path
        self.file_path_test = f.filepath()
        # inquiry and store the number of fix and record variables
        self.n_rec_vars = f.inq_num_rec_vars()
        self.n_fix_vars = f.inq_num_fix_vars()
        # inquiry record variable record block size
        self.recsize = f.inq_recsize()
        # inquiry rFile system striping size and striping count
        self.striping_size, self.striping_count = f.inq_striping()

    def test_cdf5(self):
        """testing file inq for CDF-5 file format"""
        self.assertTrue(self.nvars == 4)
        self.assertTrue(self.ndims == 4)
        self.assertTrue(self.nattrs == 2)
        self.assertTrue(self.unlimited_dim_name == 'xu')
        self.assertTrue(self.file_path_test == self.file_path)
        self.assertTrue(self.n_rec_vars == 2)
        self.assertTrue(self.n_fix_vars == 2)
    def test_cdf2(self):
        """testing file inq for CDF-2 file format"""
        self.assertTrue(self.nvars == 4)
        self.assertTrue(self.ndims == 4)
        self.assertTrue(self.nattrs == 2)
        self.assertTrue(self.unlimited_dim_name == 'xu')
        self.assertTrue(self.file_path_test == self.file_path)
        self.assertTrue(self.n_rec_vars == 2)
        self.assertTrue(self.n_fix_vars == 2)

    def test_cdf1(self):
        """testing file inq for CDF-1 file format"""
        self.assertTrue(self.nvars == 4)
        self.assertTrue(self.ndims == 4)
        self.assertTrue(self.nattrs == 2)
        self.assertTrue(self.unlimited_dim_name == 'xu')
        self.assertTrue(self.file_path_test == self.file_path)
        self.assertTrue(self.n_rec_vars == 2)
        self.assertTrue(self.n_fix_vars == 2)

    def tearDown(self):
        # remove the temporary files
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])