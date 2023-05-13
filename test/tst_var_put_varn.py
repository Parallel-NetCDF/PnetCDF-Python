import pncpy
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
from mpi4py import MPI
from utils import validate_nc_file
import argparse


file_formats = ['64BIT_DATA', '64BIT_OFFSET', None]
file_name = "tst_var_put_varn.nc"


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
xdim = 4
ydim = 10

MAX_NUM_REQS = 6
NDIMS = 2
# reference data for size >=4 (rank 0 - 3 all participated)
dataref = np.array([[3, 3, 3, 1, 1, 0, 0, 2, 1, 1],
                    [0, 2, 2, 2, 3, 1, 1, 2, 2, 2],
                    [1, 1, 2, 3, 3, 3, 0, 0, 1, 1],
                    [0, 0, 0, 2, 1, 1, 1, 3, 3, 3]], np.float32)

# reference data for 1<=size<=3
dataref[dataref >= size] = -1
class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        self._file_format = file_formats.pop(0)
        f = pncpy.File(filename=self.file_path, mode = 'w', format=self._file_format, comm=comm, info=None)
        # define dimensions and variables
        f.def_dim('x',xdim)
        f.def_dim('y',ydim)

        var1 = f.def_var('var1', pncpy.NC_FLOAT, ('x', 'y'))
        var2 = f.def_var('var2', pncpy.NC_FLOAT, ('x', 'y'))
        f.enddef()
        var1[:] = np.full((xdim, ydim), -1, dtype=np.float32)
        var2[:] = np.full((xdim, ydim), -1, dtype=np.float32)

        starts = np.zeros((MAX_NUM_REQS, NDIMS), dtype=np.int64)
        counts = np.zeros((MAX_NUM_REQS, NDIMS), dtype=np.int64)

        #initialize variable values
        if rank == 0:
            num_reqs = 4
            starts[0][0] = 0; starts[0][1] = 5; counts[0][0] = 1; counts[0][1] = 2
            starts[1][0] = 1; starts[1][1] = 0; counts[1][0] = 1; counts[1][1] = 1
            starts[2][0] = 2; starts[2][1] = 6; counts[2][0] = 1; counts[2][1] = 2
            starts[3][0] = 3; starts[3][1] = 0; counts[3][0] = 1; counts[3][1] = 3
            # rank 0 is writing the following locations: ("-" means skip)
            #               -  -  -  -  -  0  0  -  -  - 
            #               0  -  -  -  -  -  -  -  -  - 
            #               -  -  -  -  -  -  0  0  -  - 
            #               0  0  0  -  -  -  -  -  -  - 
        elif rank == 1:
            num_reqs = 6
            starts[0][0] = 0; starts[0][1] = 3; counts[0][0] = 1; counts[0][1] = 2
            starts[1][0] = 0; starts[1][1] = 8; counts[1][0] = 1; counts[1][1] = 2
            starts[2][0] = 1; starts[2][1] = 5; counts[2][0] = 1; counts[2][1] = 2
            starts[3][0] = 2; starts[3][1] = 0; counts[3][0] = 1; counts[3][1] = 2
            starts[4][0] = 2; starts[4][1] = 8; counts[4][0] = 1; counts[4][1] = 2
            starts[5][0] = 3; starts[5][1] = 4; counts[5][0] = 1; counts[5][1] = 3
            # rank 1 is writing the following locations: ("-" means skip)
            #               -  -  -  1  1  -  -  -  1  1 
            #               -  -  -  -  -  1  1  -  -  - 
            #               1  1  -  -  -  -  -  -  1  1 
            #               -  -  -  -  1  1  1  -  -  - 
        elif rank == 2:
            num_reqs = 5
            starts[0][0] = 0; starts[0][1] = 7; counts[0][0] = 1; counts[0][1] = 1
            starts[1][0] = 1; starts[1][1] = 1; counts[1][0] = 1; counts[1][1] = 3
            starts[2][0] = 1; starts[2][1] = 7; counts[2][0] = 1; counts[2][1] = 3
            starts[3][0] = 2; starts[3][1] = 2; counts[3][0] = 1; counts[3][1] = 1
            starts[4][0] = 3; starts[4][1] = 3; counts[4][0] = 1; counts[4][1] = 1
            # rank 2 is writing the following locations: ("-" means skip)
            #         -  -  -  -  -  -  -  2  -  - 
            #         -  2  2  2  -  -  -  2  2  2 
            #         -  -  2  -  -  -  -  -  -  - 
            #         -  -  -  2  -  -  -  -  -  - 
        elif rank == 3:
            num_reqs = 4
            starts[0][0] = 0; starts[0][1] = 0; counts[0][0] = 1; counts[0][1] = 3
            starts[1][0] = 1; starts[1][1] = 4; counts[1][0] = 1; counts[1][1] = 1
            starts[2][0] = 2; starts[2][1] = 3; counts[2][0] = 1; counts[2][1] = 3
            starts[3][0] = 3; starts[3][1] = 7; counts[3][0] = 1; counts[3][1] = 3
            # rank 3 is writing the following locations: ("-" means skip)
            #         3  3  3  -  -  -  -  -  -  - 
            #         -  -  -  -  3  -  -  -  -  - 
            #         -  -  -  3  3  3  -  -  -  - 
            #         -  -  -  -  -  -  -  3  3  3 
        else:
            num_reqs = 0
        # allocate write buffer
        buf_len = 0
        for i in range(num_reqs):
            w_req_len = np.prod(counts[i,:])
            buf_len += w_req_len
        data = np.empty(buf_len, dtype=np.float32)
        data.fill(rank)
        # collective put_var
        var1.put_var_all(data, start = starts, count = counts, num = num_reqs)

        # independent put_var
        f.begin_indep()
        var2.put_var(data, start = starts, count = counts, num = num_reqs)
        f.close()
        comm.Barrier()
        assert validate_nc_file(self.file_path) == 0

    def tearDown(self):
        # Remove the temporary files
        comm.Barrier()
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def runTest(self):
        """testing variable put vara all"""

        f = pncpy.File(self.file_path, 'r')
        # test collective i/o put_var
        v1 = f.variables['var1']
        assert_array_equal(v1[:], dataref)
        # test independent i/o put_var
        v2 = f.variables['var2']
        assert_array_equal(v2[:], dataref)
        f.close()

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
