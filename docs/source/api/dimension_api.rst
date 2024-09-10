==============
Dimensions
==============

Class ``Dimension`` is used to define the shape of NetCDF variables. In NetCDF,
a variable, an instance of :class:`pnetcdf.Variable`, is a multi-dimensional
array. Methods in :class:`pnetcdf.Dimension` provide an interface to access
dimensions objects stored in the file.

.. autoclass:: pnetcdf::Dimension
   :members: getfile, isunlimited
   :exclude-members: name, size

Read-only Python Attributes of Dimension Class
 The following class members are read-only and should not be modified by the
 user.

 .. attribute:: name

    String name of Dimension instance. This class member is read-only and
    should not be modified by the user. To rename a dimension, use
    :meth:`File.rename_dim` method.

    **Type:** `str`

 .. attribute:: size

    The current size of Dimension (its value can be obtained by calling
    python function ``len()`` on the Dimension instance).

    **Type:** `int`

