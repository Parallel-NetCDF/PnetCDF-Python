# demonstrate how File and Dimension work together.
# should delete in future

from mpi4py import MPI
import pncpy


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

file0 = pncpy.File(filename="test0.nc", Comm=comm, Info=None)
file = pncpy.File(filename="test.nc", Comm=comm, Info=None)
dim = pncpy.Dimension(file=file)

file.dim = dim

dim._id = 1000
print(file.dim._id)
print(file._ncid, file.dim.file._ncid)

temp_id = file._ncid
file._ncid = 1777
print(temp_id, file._ncid, file.dim.file._ncid)
file._ncid = temp_id

file.close()
file0.close()
