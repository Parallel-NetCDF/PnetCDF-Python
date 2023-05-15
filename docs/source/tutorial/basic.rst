=========
Basics
=========

.. warning::

   Under construction. 

Running Python scripts with MPI
-------------------------------

Python programs with PnetCDF-python can be run with the command :program:`mpiexec`. In
practice, running Python programs looks like:

  $ mpiexec -n 4 python script.py

to run the program with 4 processors.

Creating/Opening/Closing a netCDF file
--------------------------------------

To create a netCDF file from python, you simply call the ``File`` constructor. This is also
the method used to open an existing netCDF file. If the file is open for write access 
(mode='w', 'r+' or 'a'), you may write any type of data including new dimensions, variables 
and attributes. Currently, netCDF files can be created in classic formats, specifically the 
formats of CDF-1, 2, and 5. When creating a new file, the format may be specified using the 
format keyword in the ``File`` constructor. The default format is NETCDF4. To see how a given 
file is formatted, you can examine the ``file_format`` attribute. Closing the netCDF file is 
accomplished via the ``File.close`` method of the ``File`` instance.

Here's an example:
 .. code-block:: python

    import pncpy
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    # create a new file using "w" mode
    f = pncpy.File(filename="testfile.nc", mode = 'w', comm=comm, info=None)
    # close the file
    f.close()

Dimensions in a netCDF file
-----------------------------------

Variables in a netCDF file
----------------------------------

Attributes in a netCDF file
----------------------------------

Writing values to and reading values from a netCDF variable
-------------------------------------------------------------------

