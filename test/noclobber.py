from mpi4py import MPI
import pncpy
import os
import pncpy 

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

file_names = ["tst_noclobber1.nc", "tst_noclobber2.nc"]

for file_name in file_names:
    if os.path.exists(file_name):
        os.remove(file_name)

file = pncpy.File(filename=file_names[0], mode='w', comm=comm, info=None)
file.close()

recive_os_error = False
try:
    file = pncpy.File(filename=file_names[0], format="64BIT_DATA",
                      mode='w', clobber=False, comm=comm, info=None)
except OSError:
    recive_os_error = True

assert recive_os_error


file = pncpy.File(filename=file_names[1], format="64BIT_DATA",
                  mode='w', clobber=False, comm=comm, info=None)
file.close()
