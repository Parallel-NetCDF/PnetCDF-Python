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
file_name = "tst_var_put_vars.nc"


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
xdim=9; ydim=10; zdim=size*10
data = np.zeros((xdim,ydim,zdim)).astype('i4')
datam = randint(0,10, size=(1,3,5)).astype('i4')
datares1, datares2 = data.copy(), data.copy()

for i in range(size):
    datares1[3:4:1,0:6:2,i*10:(i+1)*10:2] = datam

for i in range(min(size,2)):
    datares2[3:4:1,0:6:2,i*10:(i+1)*10:2] = datam

class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        data_model = data_models.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=data_model, Comm=comm, Info=None)
        f.defineDim('x',xdim)
        f.defineDim('xu',-1)
        f.defineDim('y',ydim)
        f.defineDim('z',zdim)

        v1_u = f.defineVar('data1u', pncpy.NC_INT, ('xu','y','z'))
        v2_u = f.defineVar('data2u', pncpy.NC_INT, ('xu','y','z'))

        #initize variable values
        f.enddef()
        v1_u[:] = data
        v2_u[:] = data
        f.close()

        # all processes write subarray to variable with put_var_all (collective i/o)
        f = pncpy.File(filename=self.file_path, mode = 'r+', format=data_model, Comm=comm, Info=None)
        v1_u = f.variables['data1u']
        starts = np.array([3, 0, 10 * rank])
        counts = np.array([1, 3, 5])
        strides = np.array([1, 2, 2])
        v1_u.put_var_all(datam, start = starts, count = counts, stride = strides)
        #Optional put_var(*args) make all starts, counts, strides arguments optional
        #Check condition of arguments
        #Compare i/o performance 

        # write subarray to variable with put_var (independent i/o)
        v2_u = f.variables['data2u']
        f.begin_indep()
        if rank < 2:
            v2_u.put_var(datam, start = starts, count = counts, stride = strides)
        f.end_indep()
        f.close()
        comm.Barrier()
        assert validate_nc_file(self.file_path) == 0

    def tearDown(self):
        # Remove the temporary files
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def test_cdf5(self):
        """testing variable put var all"""

        f = pncpy.File(self.file_path, 'r')
        # test collective i/o put_var
        f.enddef()
        v1 = f.variables['data1u']
        assert_array_equal(v1[:], datares1)
        # test independent i/o put_var
        v2 = f.variables['data2u']
        assert_array_equal(v2[:], datares2)
        f.close()

    def test_cdf2(self):
        """testing variable put var all"""
        f = pncpy.File(self.file_path, 'r')
        # test collective i/o put_var
        v1 = f.variables['data1u']
        assert_array_equal(v1[:], datares1)
        # test independent i/o put_var
        v2 = f.variables['data2u']
        assert_array_equal(v2[:], datares2)
        f.close()

    def test_cdf1(self):
        """testing variable put var all"""
        f = pncpy.File(self.file_path, 'r')
        # test collective i/o put_var
        v1 = f.variables['data1u']
        assert_array_equal(v1[:], datares1)
        # test independent i/o put_var
        v2 = f.variables['data2u']
        assert_array_equal(v2[:], datares2)
        f.close()



if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])