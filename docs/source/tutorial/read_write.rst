.. currentmodule:: pnetcdf
============================
Parallel Read and Write
============================

NumPy Slicing Syntax
--------------------------------------

 PnetCDF-python datasets re-use the numpy slicing syntax to read and write to
 the file. Slice specifications are translated directly to PnetCDF “start,
 count, stride” selections, and are a fast and efficient way to access data in
 the file. The following slicing arguments are recognized:

 - Indices (var[1,5])
 - Slices (i.e. [:] or [0:10])
 - An empty tuple (()) to retrieve all data
 - Multiple indexing (e.g. var[1][5]) is NOT SUPPORTED in write

 The operational mode (collective/independent) is dependent on the current file
 mode status.

 .. code-block:: Python

    f.enddef() # Exit define mode

    var = f.variables['var']
    buff = np.zeros(shape = (10, 50), dtype = "i4")

    # put values to the entire variable
    var[:] = buff

    # read the topleft 10*10 corner from variable var
    print(var[:10, :10])


Method Call of put_var()/get_var()
--------------------------------------

 Using specific method calls to perform I/O is particularly useful in
 multi-processing programs. :meth:`Variable.put_var` requires `data` as a
 mandatory argument, which serves as a write buffer that stores values to be
 written. :meth:`Variable.get_var` requires `buff` as a mandatory argument,
 which serves as a read buffer that stores values to be read. The behavior of
 :meth:`Variable.put_var` and :meth:`Variable.get_var` varies depending on the
 pattern of provided optional arguments - `index`, `start`, `count`, `stride`,
 and `imap`. The suffix `_all` indicates this is collective I/O in contrast to
 independent I/O (without `_all`).

Read from netCDF variables
 For reading, the behavior of :meth:`Variable.get_var` depends on the following
 provided input parameter pattern:

 - `buff` - Read an entire variable
 - `buff`, `index` - Read a single data value
 - `buff`, `start`, `count` - Read an array of values
 - `buff`, `start`, `count`, `stride` - Read a subarray of values
 - `buff`, `start`, `count`, `imap`, `buff` - Read a mapped array of values

 where `start`, `count` and `stride` represent a corner, a vector of edge
 lengths, and a stride vector respectively. Together, they specify a subarray
 section to read from in a netCDF variable as illustrated in the diagram below.
 By default, the method returns a multidimensional numpy array in the shape of
 (count[0], ... count[n-1]).

 .. image:: get_vars.png
   :width: 500
   :align: center

 Here's a python example:

 .. code-block:: Python

    # Collectively read from a subarray of a variable
    buf = var.get_var_all(start = [0, 0], count = [5, 25], stride = [2,2])

    # Independently read from a subarray of a variable
    f.end_indep()
    buf = var.get_var(start = [0, 0], count = [5, 25], stride = [2,2])

 For full example program, see ``examples/get_var.py``.

Write to netCDF variables
 For writing, the behavior of :meth:`Variable.put_var` depends on the following
 provided input parameter pattern:

 - `data` - Write an entire variable
 - `data`, `index` - Write a single data value (a single element)
 - `data`, `start`, `count` - Write an array of values
 - `data`, `start`, `count`, `stride` - Write a subarray of values
 - `data`, `start`, `count`, `imap` - Write a mapped array of values

 where `start`, `count` and `stride` represent a corner, a vector of edge
 lengths, and a stride vector respectively. Together, they specify a subarray
 section to write to for a netCDF variable as illustrated in the diagram below.
 Note that the buffer array (the numpy array to write) can take any shape as
 long as the total size is matched with `count`.

 .. image:: put_vars.png
   :width: 500
   :align: center

 Here's a python example:

 .. code-block:: Python

    # Collectively write to a subarray of a variable
    buff = np.zeros(shape = (5, 25), dtype = "i4")
    var.put_var_all(buff, start = [0, 0], count = [5, 25], stride = [2,2])

    # Independently write to a subarray of a variable
    f.end_indep()
    var.put_var(buff, start = [0, 0], count = [5, 25], stride = [2,2])

 For the full example program, see ``examples/put_var.py`` and ``examples/collective_write.py``.


