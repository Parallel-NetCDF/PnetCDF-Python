==============
Dimension
==============

Dimension defines the shape and structure of variables and stores coordinate
data for multidimensional arrays. The ``Dimension`` object, which is also a key
component of ``File`` class, provides an interface to access dimensions.

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

    The current size of Dimension (calls ``len`` on Dimension instance).

    **Type:** `int`

