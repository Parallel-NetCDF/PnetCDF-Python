# This file is part of pncpy, a Python interface to the PnetCDF library.
#
#
# Copyright (C) 2023, Northwestern University
# See COPYRIGHT notice in top-level directory
# License:  

"""
   This example program is intended to illustrate the use of the pnetCDF python API.
   It is a program which writes and reads string arrays to/from netCDF variables using indexer
   operators (numpy array style). When writing with indexer syntax, the library internally will 
   invoke ncmpi_put_vara/vars. Similarly when reading with indexer syntax the library internally 
   will invoke ncmpi_get_vara/vars

   To run the test, execute the following
    `mpiexec -n [num_process] python3 tst_var_indexer.py [test_file_output_dir](optional)`

"""
import pncpy
from numpy.random import seed, randint
from numpy.testing import assert_array_equal, assert_equal, assert_array_almost_equal
import tempfile, unittest, os, random, sys
import numpy as np
import random, string
from mpi4py import MPI
from utils import validate_nc_file
from pncpy import stringtochar, chartostring
import copy


seed(0)
random.seed(0)
def generateString(length, alphabet=string.ascii_letters + string.digits + string.punctuation):
    return(''.join([random.choice(alphabet) for i in range(length)]))


# Format of the data file we will create (64BIT_DATA for CDF-5 and 64BIT_OFFSET for CDF-2 and None for CDF-1)
file_formats = ['64BIT_DATA', '64BIT_OFFSET', None]

# Name of the test data file
file_name = "tst_var_string.nc"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


n2 = 20; nchar = 12; nrecs = 4
data = np.empty((nrecs,n2),'S'+repr(nchar))
for nrec in range(nrecs):
    for n in range(n2):
        data[nrec,n] = generateString(nchar)
datau = data.astype('U').copy()
datac = stringtochar(data, encoding='ascii')

class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], file_name)
        else:
            self.file_path = file_name
        self._file_format = file_formats.pop(0)
        # Create the test data file 
        f = pncpy.File(filename=self.file_path, mode = 'w', format=self._file_format, comm=comm, info=None)
        # Define dimensions needed, one of the dims is unlimited
        f.def_dim('n1',-1)
        f.def_dim('n2',n2)
        f.def_dim('nchar',nchar)
        # We are writing 3D data on a unlimited x 20 x 4 grid 
        v1 = f.def_var('string1', pncpy.NC_CHAR, ('n1','n2','nchar'))
        v2 = f.def_var('string2', pncpy.NC_CHAR, ('n1','n2','nchar'))
        v3 = f.def_var('string3', pncpy.NC_CHAR, ('n1','n2','nchar'))
        # if _Encoding set, string array should automatically be converted to a char array
        f.set_fill(pncpy.NC_FILL)
 
        v2._Encoding = 'ascii'
        v3._Encoding = 'ascii'
   
        f.enddef()
        for nrec in range(nrecs):
            datac = stringtochar(data,encoding='ascii')
            v1[nrec] = datac[nrec]

        v2[:-1] = data[:-1]
        v2[-1] = data[-1]
        v2[-1,-1] = data[-1,-1] # write single element
        v2[-1,-1] = data[-1,-1].tobytes() # write single python string
        # _Encoding should be ignored if an array of characters is specified
        v3[:] = stringtochar(data, encoding='ascii')
        f.close()

        # Validate the created data file using ncvalidator tool
        assert validate_nc_file(self.file_path) == 0
        

    def tearDown(self):
        # Wait for all processes to finish testing (in multiprocessing mode)
        comm.Barrier()
        # Remove testing file
        if (rank == 0) and not((len(sys.argv) == 2) and os.path.isdir(sys.argv[1])):
            os.remove(self.file_path)

    def runTest(self):
        """testing functions for converting arrays of chars to fixed-len strings"""

        f = pncpy.File(filename=self.file_path, mode = 'r')
        assert f.dimensions['n1'].isunlimited() == True
        v = f.variables['string1']
        v2 = f.variables['string2']
        v3 = f.variables['string3']
        assert v.dtype.str[1:] in ['S1','U1']
        assert v.shape == (nrecs,n2,nchar)
        for nrec in range(nrecs):
            data2 = chartostring(v[nrec],encoding='ascii')
            assert_equal(data2.flatten(),datau[nrec].flatten())
        data2 = v2[:]
        data2[0] = v2[0]
        data2[0,1] = v2[0,1]
        assert_array_equal(data2,datau)
        data3 = v3[:]
        assert_array_equal(data3,datau)
        # these slices should return a char array, not a string array
        data4 = v2[:,:,0]
        assert(data4.dtype.itemsize == 1)
        assert_array_equal(data4, datac[:,:,0])
        data5 = v2[0,0:nchar,0]
        assert(data5.dtype.itemsize == 1)
        assert_array_equal(data5, datac[0,0:nchar,0])
        # test turning auto-conversion off.
        v2.set_auto_chartostring(False)
        data6 = v2[:]
        assert(data6.dtype.itemsize == 1)
        assert_array_equal(data6, datac)
        f.set_auto_chartostring(False)
        data7 = v3[:]
        assert(data7.dtype.itemsize == 1)
        assert_array_equal(data7, datac)
        f.close()

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for i in range(len(file_formats)):
        suite.addTest(VariablesTestCase())
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

