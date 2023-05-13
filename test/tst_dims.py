import sys
import unittest
import os
import tempfile
from numpy.random.mtrand import uniform
from mpi4py import MPI
import pncpy
from utils import validate_nc_file


NUM_TESTS = 5
file_formats = [fmt for fmt in ['64BIT_DATA', '64BIT_OFFSET', None] for i in range(NUM_TESTS)]
FILE_NAME = "tst_dims.nc"

LAT_NAME="lat"
LAT_LEN = 50
LON_NAME="lon"
LON_LEN = 100
LEVEL_NAME="level"
LEVEL_LEN = -1
LEVEL_LENG = -1
TIME_NAME="time"
TIME_LEN = 60
TIME_LENG = -1
GROUP_NAME='forecasts'
VAR_NAME1='temp1'
VAR_NAME2='temp2'
VAR_NAME3='temp3'
VAR_NAME4='temp4'
VAR_NAME5='temp5'
VAR_TYPE= pncpy.NC_DOUBLE

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

class DimensionsTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], FILE_NAME)
        else:
            self.file_path = FILE_NAME
        self._file_format = file_formats.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=self._file_format, comm=comm, info=None)
        lat_dim=f.def_dim(LAT_NAME,LAT_LEN)
        lon_dim=f.def_dim(LON_NAME,LON_LEN)
        lev_dim=f.def_dim(LEVEL_NAME,LEVEL_LEN)
        time_dim=f.def_dim(TIME_NAME,TIME_LEN)

        # specify dimensions with names
        fv1 = f.def_var(VAR_NAME1,VAR_TYPE,(LEVEL_NAME, LAT_NAME, LON_NAME, TIME_NAME))
        # specify dimensions with instances
        fv2 = f.def_var(VAR_NAME2,VAR_TYPE,(lev_dim,lat_dim,lon_dim,time_dim))
        # specify dimensions using a mix of names and instances
        fv3 = f.def_var(VAR_NAME3,VAR_TYPE,(lev_dim, LAT_NAME, lon_dim, TIME_NAME))
        # single dim instance for name (not in a tuple)
        fv4 = f.def_var(VAR_NAME4,VAR_TYPE,time_dim)
        fv5 = f.def_var(VAR_NAME5,VAR_TYPE,TIME_NAME)
        f.close()
        assert validate_nc_file(self.file_path) == 0

 
    
    def tearDown(self):
        # Remove the temporary file
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def test_dim_name(self):
        f  = pncpy.File(self.file_path, 'r+')
        v1 = f.variables[VAR_NAME1]
        v2 = f.variables[VAR_NAME2]
        v3 = f.variables[VAR_NAME3]
        v4 = f.variables[VAR_NAME4]
        v5 = f.variables[VAR_NAME5]
        isunlim = [dim.isunlimited() for dim in f.dimensions.values()]

        dimlens = [len(dim) for dim in f.dimensions.values()]
        names_check = [LAT_NAME, LON_NAME, LEVEL_NAME, TIME_NAME]
        lens_check = [LAT_LEN, LON_LEN, LEVEL_LEN, TIME_LEN]
        isunlim = [dimlen == -1 for dimlen in lens_check]
        for n,dimlen in enumerate(lens_check):
            if dimlen == -1:
                lens_check[n] = 0
        lensdict = dict(zip(names_check,lens_check))
        unlimdict = dict(zip(names_check,isunlim))
        # check that dimension names are correct.
        for name in f.dimensions.keys():
            self.assertTrue(name in names_check)
        for name in v1.dimensions:
            self.assertTrue(name in names_check)
        for name in v2.dimensions:
            self.assertTrue(name in names_check)
        for name in v3.dimensions:
            self.assertTrue(name in names_check)
        self.assertTrue(v4.dimensions[0] == TIME_NAME)
        self.assertTrue(v5.dimensions[0] == TIME_NAME)
        f.close()

    def test_dim_len(self):
        f  = pncpy.File(self.file_path, 'r+')

        v1 = f.variables[VAR_NAME1]
        v2 = f.variables[VAR_NAME2]
        v3 = f.variables[VAR_NAME3]
        v4 = f.variables[VAR_NAME4]
        v5 = f.variables[VAR_NAME5]
        isunlim = [dim.isunlimited() for dim in f.dimensions.values()]

        dimlens = [len(dim) for dim in f.dimensions.values()]
        names_check = [LAT_NAME, LON_NAME, LEVEL_NAME, TIME_NAME]
        lens_check = [LAT_LEN, LON_LEN, LEVEL_LEN, TIME_LEN]
        isunlim = [dimlen == -1 for dimlen in lens_check]
        for n,dimlen in enumerate(lens_check):
            if dimlen == -1:
                lens_check[n] = 0
        lensdict = dict(zip(names_check,lens_check))
        unlimdict = dict(zip(names_check,isunlim))
        # check that dimension lengths are correct.
        for name,dim in f.dimensions.items():
            self.assertTrue(len(dim) == lensdict[name])
        f.close()

    def test_isunlimited(self):
        f  = pncpy.File(self.file_path, 'r+')

        v1 = f.variables[VAR_NAME1]
        v2 = f.variables[VAR_NAME2]
        v3 = f.variables[VAR_NAME3]
        v4 = f.variables[VAR_NAME4]
        v5 = f.variables[VAR_NAME5]
        isunlim = [dim.isunlimited() for dim in f.dimensions.values()]

        dimlens = [len(dim) for dim in f.dimensions.values()]
        names_check = [LAT_NAME, LON_NAME, LEVEL_NAME, TIME_NAME]
        lens_check = [LAT_LEN, LON_LEN, LEVEL_LEN, TIME_LEN]
        isunlim = [dimlen == -1 for dimlen in lens_check]
        dimlens = [len(dim) for dim in f.dimensions.values()]
        names_check = [LAT_NAME, LON_NAME, LEVEL_NAME, TIME_NAME]
        lens_check = [LAT_LEN, LON_LEN, LEVEL_LEN, TIME_LEN]
        isunlim = [dimlen == -1 for dimlen in lens_check]
        for n,dimlen in enumerate(lens_check):
            if dimlen == -1:
                lens_check[n] = 0
        lensdict = dict(zip(names_check,lens_check))
        unlimdict = dict(zip(names_check,isunlim))
        # check that isunlimited() method works.
        for name,dim in f.dimensions.items():
            self.assertTrue(dim.isunlimited() == unlimdict[name])
        f.close()

    def test_len_var(self):
        # add some data to variable along unlimited dims,
        # make sure length of dimensions change correctly.
        f  = pncpy.File(self.file_path, 'r+')

        v1 = f.variables[VAR_NAME1]
        v2 = f.variables[VAR_NAME2]
        v3 = f.variables[VAR_NAME3]
        v4 = f.variables[VAR_NAME4]
        v5 = f.variables[VAR_NAME5]
        isunlim = [dim.isunlimited() for dim in f.dimensions.values()]

        dimlens = [len(dim) for dim in f.dimensions.values()]
        names_check = [LAT_NAME, LON_NAME, LEVEL_NAME, TIME_NAME]
        lens_check = [LAT_LEN, LON_LEN, LEVEL_LEN, TIME_LEN]
        isunlim = [dimlen == -1 for dimlen in lens_check]
        dimlens = [len(dim) for dim in f.dimensions.values()]
        names_check = [LAT_NAME, LON_NAME, LEVEL_NAME, TIME_NAME]
        lens_check = [LAT_LEN, LON_LEN, LEVEL_LEN, TIME_LEN]
        isunlim = [dimlen == -1 for dimlen in lens_check]
        for n,dimlen in enumerate(lens_check):
            if dimlen == -1:
                lens_check[n] = 0
        lensdict = dict(zip(names_check,lens_check))
        nadd1 = 2
        v1[0:nadd1,:,:,:] = uniform(size=(nadd1,LAT_LEN,LON_LEN,TIME_LEN))
        lensdict[LEVEL_NAME]=nadd1
        # check that dimension lengths are correct.
        for name,dim in f.dimensions.items():
            self.assertTrue(len(dim) == lensdict[name])
        f.close()


    def test_get_dims(self):

        # check get_dims variable method
        f  = pncpy.File(self.file_path, 'r+')
        
        v1 = f.variables[VAR_NAME1]
        v2 = f.variables[VAR_NAME2]
        v3 = f.variables[VAR_NAME3]
        v4 = f.variables[VAR_NAME4]
        v5 = f.variables[VAR_NAME5]
        isunlim = [dim.isunlimited() for dim in f.dimensions.values()]

        dimlens = [len(dim) for dim in f.dimensions.values()]
        names_check = [LAT_NAME, LON_NAME, LEVEL_NAME, TIME_NAME]
        lens_check = [LAT_LEN, LON_LEN, LEVEL_LEN, TIME_LEN]
        isunlim = [dimlen == -1 for dimlen in lens_check]
        for n,dimlen in enumerate(lens_check):
            if dimlen == -1:
                lens_check[n] = 0
        lensdict = dict(zip(names_check,lens_check))
        unlimdict = dict(zip(names_check,isunlim))
        dim_tuple = v1.get_dims()
        dim_tup1 = (f.dimensions['level'],f.dimensions['lat'],\
                    f.dimensions['lon'],f.dimensions['time'])
        dim_tup2 = v1.get_dims()
        assert(dim_tup1 == dim_tup2)
        f.close()
        

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats) // NUM_TESTS):
        suite.addTest(DimensionsTestCase("test_dim_name"))
        suite.addTest(DimensionsTestCase("test_dim_len"))
        suite.addTest(DimensionsTestCase("test_isunlimited"))
        suite.addTest(DimensionsTestCase("test_len_var"))
        suite.addTest(DimensionsTestCase("test_get_dims"))
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

