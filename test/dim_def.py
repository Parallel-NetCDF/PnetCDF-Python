from mpi4py import MPI
import pncpy
from utils import validate_nc_file


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

FILE_NAME = "tst_dim_create.nc"

file1 = pncpy.File(filename=FILE_NAME, mode='w', comm=comm, info=None)
file1.def_dim(dimname = "dummy_dim1", size = 3)
file1.def_dim(dimname = "dummy_dim2", size = -1)
print(file1.dimensions)
file1.close()

assert validate_nc_file(FILE_NAME) == 0

