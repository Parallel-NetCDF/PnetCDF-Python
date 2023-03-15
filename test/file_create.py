from mpi4py import MPI
import pncpy
from utils import validate_nc_file

FILE_NAME = "tst_file_create.nc"
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

file = pncpy.File(filename=FILE_NAME, Comm=comm, Info=None)
file.close()


assert validate_nc_file(FILE_NAME) == 0