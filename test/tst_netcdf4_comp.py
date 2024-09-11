from mpi4py import MPI
import pnetcdf
from netCDF4 import Dataset


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
# Create two files with pnetcdf-python and copy attributes from one file to another
f0 = pnetcdf.File("tmp_test0.nc",'w', format = None, comm = comm)
f1 = pnetcdf.File("tmp_test1.nc",'w', format = None, comm = comm)

v0 = f0.def_var('var0', 'i4', ())
v1 = f1.def_var('var1', 'i4', ())

f0.put_att('history','today')
v0.put_att('history','today')
att = f0.get_att("history")
v_att = v0.get_att("history")
f1.put_att('history', att)
v1.put_att('history', v_att)
f0.close()
f1.close()

# Create the file with netCDF4-python 
rootgrp = Dataset("test.nc", "w", format="NETCDF4")
dim0 = rootgrp.createDimension("x", 10)
rootgrp.close()