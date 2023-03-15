from mpi4py import MPI
import pncpy
from utils import validate_nc_file


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

FILE_NAME = "var_def.nc"

file1 = pncpy.File(filename=FILE_NAME, mode='w', Comm=comm, Info=None)
file1.redef()
file1.defineDim(dimname = "dummy_dim1", size = 3)
file1.defineDim(dimname = "dummy_dim2", size = -1)
print(file1.dimensions)


varname = "dummy_var1"
datatype = pncpy.NC_INT
file1.defineVar(varname, datatype, dimensions=("dummy_dim2", "dummy_dim1"), fill_value=None)
print(file1.variables)
file1.enddef()
file1.close()

assert validate_nc_file(FILE_NAME) == 0

