from mpi4py import MPI
import pncpy
import numpy as np
from utils import validate_nc_file

FILE_NAME = "tst_att_create.nc"
file_format = '64BIT_OFFSET'
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

file1 = pncpy.File(filename=FILE_NAME, mode='w', format=self._file_format, comm=comm, info=None)
file1.redef()
file1.dummy_attr1 = np.int32(10) if file_format != "64BIT_DATA" else 10
setattr(file1, "dummy_attr2", "attibute2")
print(vars(file1))

file1.height = np.int32(123) if file_format != "64BIT_DATA" else 123
print(vars(file1))

file1.time = [1.2, 2.3, 3.4]
print(vars(file1))

file1.rename_att(oldname = "dummy_attr2", newname = "dummy_attr3")
print(vars(file1))

delattr(file1, 'dummy_attr1')
print(vars(file1))
file1.enddef()

file1.close()
assert validate_nc_file(FILE_NAME) == 0