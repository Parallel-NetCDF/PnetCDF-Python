=========
Variables
=========

``Variable`` is a core component of a netCDF file representing an array of data
values organized along one or more dimensions, with associated metadata in the
form of attributes. An instance of class :class:`pnetcdf.Variable` represents a
NetCDF variable stored in the file. The class methods provide I/O operations to
read and write the data and metadata of a NetCDF variable.

Reading and writing a subarray of a variable can be done through either
explicit function-call style methods or Python indexer-style (numpy-like)
syntax.

.. autoclass:: pnetcdf::Variable
   :members: ncattrs, put_att, get_att, del_att, rename_att, get_dims,
    def_fill, inq_fill, fill_rec, set_auto_chartostring, put_var, put_var_all,
    get_var, get_var_all, iput_var, bput_var iget_var, inq_offset
   :exclude-members: name, dtype, datatype, shape, ndim, size, dimensions,
    chartostring


Read-only python fields of class :class:`pnetcdf.Variable`
    The following class fields are read-only and should not be modified
    directly by the user.

    .. attribute:: name

       The string name of Variable instance

       **Type:** `str`

    .. attribute:: dtype

       A numpy data type of the variable.

       **Type:** ``numpy.dtype``

    .. attribute:: datatype

       Same as :meth:`Variable.dtype`.

       **Type:** ``numpy.dtype``

    .. attribute:: shape

       The shape of the variable, which is the current sizes of all variable
       dimensions

       **Type:** `tuple of ints`

    .. attribute:: ndim

       The number of variable dimensions.

       **Type:** `int`

    .. attribute:: size

       Return the number of stored elements

       **Type:** `int`

    .. attribute:: dimensions

       Return the variable's dimension names

       **Type:** `list of str`

    .. attribute:: chartostring

       If `True`, data is automatically converted to/from character arrays to
       string arrays when the `_Encoding` variable attribute is set. Default
       is `True`, can be reset using :meth:`Variable.set_auto_chartostring`
       method.

       **Type:** `bool`

