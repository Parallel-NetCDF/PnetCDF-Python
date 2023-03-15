import math
import subprocess
import sys
import unittest
import os
import tempfile
import warnings
import math

import numpy as np
from collections import OrderedDict
from numpy.random.mtrand import uniform
from utils import validate_nc_file
from mpi4py import MPI
import pncpy

# test attribute creation.
#FILE_NAME = tempfile.NamedTemporaryFile(suffix='.nc', delete=False).name
FILE_NAME = 'tst_atts.nc'
VAR_NAME="dummy_var"
DIM1_NAME="x"
DIM1_LEN=2
DIM2_NAME="y"
DIM2_LEN=3
DIM3_NAME="z"
DIM3_LEN=25
STRATT = 'string attribute'
EMPTYSTRATT = ''
INTATT = 1
FLOATATT = math.pi
SEQATT = np.arange(10)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


#ATTDICT = {'stratt':STRATT,'floatatt':FLOATATT,'seqatt':SEQATT,
#           'stringseqatt':''.join(STRINGSEQATT), # changed in issue #770
#           'emptystratt':EMPTYSTRATT,'intatt':INTATT}
ATTDICT = {'stratt':STRATT,'floatatt':FLOATATT,'seqatt':SEQATT,
           'emptystratt':EMPTYSTRATT,'intatt':INTATT}

class VariablesTestCase(unittest.TestCase):

    def setUp(self):
        if (len(sys.argv) == 2) and os.path.isdir(sys.argv[1]):
            self.file_path = os.path.join(sys.argv[1], FILE_NAME)
        else:
            self.file_path = FILE_NAME
        with pncpy.File(self.file_path,'w', format = "64BIT_DATA") as f:
            # try to set a dataset attribute with one of the reserved names.
            f.setncattr('data_model','netcdf5_format')
            # test attribute renaming
            f.stratt_tmp = STRATT
            f.renameAttribute('stratt_tmp','stratt')
            f.emptystratt = EMPTYSTRATT
            f.floatatt = FLOATATT
            f.intatt = INTATT
            f.seqatt = SEQATT
            # sequences of strings converted to a single string.
            f.defineDim(DIM1_NAME, DIM1_LEN)
            f.defineDim(DIM2_NAME, DIM2_LEN)
            f.defineDim(DIM3_NAME, DIM3_LEN)

            v = f.defineVar(VAR_NAME, pncpy.NC_DOUBLE, (DIM1_NAME,DIM2_NAME,DIM3_NAME))
            # try to set a variable attribute with one of the reserved names.
            v.setncattr('ndim','three')
            v.setncatts({'foo': 1})
            v.setncatts(OrderedDict(bar=2))
            v.stratt_tmp = STRATT
            v.renameAttribute('stratt_tmp','stratt')
            v.emptystratt = EMPTYSTRATT
            v.intatt = INTATT
            v.floatatt = FLOATATT
            v.seqatt = SEQATT
            # issue #959: should not be able to set _FillValue after var creation
            try:
                v._FillValue(-999.)
            except AttributeError:
                pass
            else:
                raise ValueError('This test should have failed.')
            try:
                v.setncattr('_FillValue',-999.)
            except AttributeError:
                pass
            else:
                raise ValueError('This test should have failed.')
            f.foo = np.array('bar','S')
            f.foo = np.array('bar','U')
        assert validate_nc_file(self.file_path) == 0


    def tearDown(self):
        # Remove the temporary files
        #pass
        if (rank == 0) and (self.file_path == FILE_NAME):
            os.remove(self.file_path)
    
    def test_file_attr_dict_(self):
        with pncpy.File(self.file_path, 'r') as f:
            # check __dict__ method for accessing all netCDF attributes.

            for key,val in ATTDICT.items():
                if type(val) == np.ndarray:
                    assert f.__dict__[key].tolist() == val.tolist()
                else:
                    assert f.__dict__[key] == val
    def test_attr_access(self):
        with pncpy.File(self.file_path, 'r') as f:
            v = f.variables[VAR_NAME]
            # check accessing individual attributes.
            assert f.intatt == INTATT
            assert f.floatatt == FLOATATT
            assert f.stratt == STRATT
            assert f.emptystratt == EMPTYSTRATT
            # check accessing variable individual attributes.
            assert v.intatt == INTATT
            assert v.floatatt == FLOATATT
            assert v.stratt == STRATT
            assert v.seqatt.tolist() == SEQATT.tolist()
            assert v.getncattr('ndim') == 'three'
            assert v.getncattr('foo') == 1
            assert v.getncattr('bar') == 2

    def test_var_attr_dict_(self):
        with pncpy.File(self.file_path, 'r') as f:
            v = f.variables[VAR_NAME]

            # variable attributes.
            # check __dict__ method for accessing all netCDF attributes.
            for key,val in ATTDICT.items():
                if type(val) == np.ndarray:
                    assert v.__dict__[key].tolist() == val.tolist()
                else:
                    assert v.__dict__[key] == val


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])
