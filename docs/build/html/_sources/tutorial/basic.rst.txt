=========
Basics
=========

.. warning::

   Under construction. 

Running Python scripts with MPI
-------------------------------

 Python programs with PnetCDF-Python can be run with the command :program:`mpiexec`. In
 practice, running Python programs looks like:

  $ mpiexec -n 4 Python script.py

 to run the program with 4 processors.

Creating/Opening/Closing a netCDF file
--------------------------------------

 To create a netCDF file from Python, you simply call the ``File`` constructor. This is also
 the method used to open an existing netCDF file. If the file is open for write access 
 (mode='w', 'r+' or 'a'), you may write any type of data including new dimensions, variables 
 and attributes. Currently, netCDF files can be created in classic formats, specifically the 
 formats of CDF-1, 2, and 5. When creating a new file, the format may be specified using the 
 format keyword in the ``File`` constructor. The default format is CDF-1. To see how a given 
 file is formatted, you can examine the ``file_format`` attribute. Closing the netCDF file is 
 accomplished via the ``File.close`` method of the ``File`` instance.

 Here's an example:

 .. code-block:: Python

    import pncpy
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    # create a new file using "w" mode
    f = pncpy.File(filename="testfile.nc", mode = 'w', comm=comm, info=None)
    # close the file
    f.close()

 For the full example program, see ``examples/craete_open.py``.

Dimensions 
-------------

 NetCDF specifies the sizes of variables based on dimensions. Therefore, before creating any variables,
 the dimensions they depend on must be established. To create a dimension, the :func:`File.def_dim` method is called 
 on a File instance under define mode. The dimension's name is set using a Python string, while the size 
 is defined using an integer value. To create an unlimited dimension (a dimension that can be expanded), 
 the size can be omitted or assigned as -1. A "Dimension" object will be returned as a handler for this 
 dimension. 

 Here's an example:

 .. code-block:: Python

    LAT_NAME="lat"
    LAT_LEN = 50
    TIME_NAME="time"
    f = pncpy.File(filename="tmp.nc", mode = 'w', format="64BIT_DATA", comm=comm, info=None)
    lat_dim = f.def_dim(LAT_NAME,LAT_LEN)
    time_dim = f.def_dim(TIME_NAME,-1)

 All of the Dimension instances are stored in a dictionary as an Python attribute of File. 

 .. code-block:: Python

    >>> print(f.dimensions)
    {'lat': <class 'pncpy._Dimension.Dimension'>: name = 'lat', size = 50, 'time': <class 'pncpy._Dimension.Dimension'> (unlimited): name = 'time', size = 0}

 To retrieve the previous defined dimension instance from the file, you can directly index the dictionary using variable name as the key.
 The dimension information can be retrieved using following functions. 

 .. code-block:: Python

    lat_dim = f.dimensions['lat']
    print(len(lat_dim)) # current size of the dimension
    print(lat_dim.isunlimited()) # check if the dimension is unlimited

 For the full example program, see ``test/tst_dim.py``.

Variables
------------

 NetCDF variables are similar to multidimensional array objects in Python provided by the numpy module. To define a netCDF 
 variable, you can utilize the :func:`File.def_var` method within a File instance under define mode. The mandatory arguments for
 this methods include the variable name (a string in Python) and dimensions (either a tuple of dimension names or dimension 
 instances). In addition, the user need to specify the datatype of the variable using module-level NC constants (e.g. pncpy.NC_INT).
 The supported datatypes given each file format can be found :ref:`here<Datatype>`.

 Here's an example:
 
 .. code-block:: Python

    var = f.def_var("var", pncpy.NC_INT, ("time", "lat"))

 All of the variables in the file are stored in a Python dictionary, in the same way as the dimensions. To retrieve the previous defined
 netCDF variable instance from the file, you can directly index the dictionary using variable name as the key.

 .. code-block:: Python

    >>> print
    unlimited dimensions: time
    current shape = (0, 50)
   
 
 Up to this point a netCDF variable is properly defined. To write data to or read from this variable, see later sections for more details.

Attributes 
------------

 In a netCDF file, there are two types of attributes: global attributes and variable attributes. 
 Global attributes are usually related to the netCDF file as a whole and may be used for purposes 
 such as providing a title or processing history for a netCDF file.Variable attributes are used to specify 
 properties as units, special values, maximum and minimum valid values, scaling factors, and offsets. 

 Attributes for a netCDF file are defined when the file is first created, while the netCDF dataset is in 
 define mode. Additional attributes may be added later by reentering define mode. Attributes can take 
 the form of strings, numbers, or sequences. Returning to our example,

 .. code-block:: Python

    # set global attributes
    f.floatatt = math.pi # Option1: Python attribute assignment 
    f.put_att("intatt", np.int32(1)) # Option2: method put_att()
    f.seqatt = np.int32(np.arange(10))

    # set variable attributes
    var = f.variables['var'] 
    var.floatatt = math.pi 
    var.put_att("int_att", np.int32(1)) 
    var.seqatt = np.int32(np.arange(10))

 The :func:`File.ncattrs` method of a File or Variable instance can be used to retrieve the names of all 
 the netCDF attributes. And the __dict__ attribute of a File or Variable instance provides all the netCDF 
 attribute name/value pairs in a python dictionary: 

 .. code-block:: Python
   
    >>> print(var.ncattrs())
    ['floatatt', 'intatt', 'seqatt', 'int_att']
    >>> print(var.__dict__)
    {'floatatt': 3.141592653589793, 'intatt': 1, 'seqatt': array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=int32), 'int_att': 1}


 For the full example program, see ``examples/global_attributes.py``.

Writing to variable
--------------------

 Now that you have a netCDF Variable instance, how do you put data into it? Firstly make sure the file is in data mode.
 Then for writing, there are currently two options:

Option1 Indexer (or slicing) syntax 
 You can just treat it the variable like an numpy array and assign data
 to a slice. Slices are specified as a `start:stop:step` triplet.

 .. code-block:: Python

    buff = np.zeros(shape = (10, 50), dtype = "i4")
    var[:] = buff # put values to the variable


Option2 Method calls of put/get_var() 
 Alternatively you can also leverage Variable.put/get_var() method of a Variable instance
 to perform i/o according to specfic access pattern needs.

 Here is an example to write an array to the netCDF variable. The part of the netCDF variable to write is specified by giving a corner (`start`)
 and a vector of edge lengths (`count`) that refer to an array section of the netCDF variable. 

 .. code-block:: Python

    buff = np.zeros(shape = (10, 50), dtype = "i4")
    var.put_var_all(buff, start = [10, 0], count = [10, 50]) # Equivalent to var[10:20, 0:50] = buff


Reading from variable
----------------------

 Symmetrically, users can use two options with different syntaxes to retreive array values from the variable.

 .. code-block:: Python

    var = f.variables['var'] 
    print(var[:10, :10]) # Option1 Indexer: read the topleft 10*10 corner from variable var 
    print(var.get_var_all(start = [10, 0], count = [10, 50])) # Option2 Method Call: equivalent to var[10:20, 0:50]
    
 Similarly, :func:`Variable.get_var()` takes the same set of optional arguments and behave differently depending on the pattern of provided
 optional arguments. 
 
 To learn more about reading and writing, see the :ref:`here<Parallel Read and Write>` page.