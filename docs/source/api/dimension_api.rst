.. currentmodule:: pnetcdfpy
==============
Dimension
==============

Dimension defines the shape and structure of variables and stores 
coordinate data for multidimensional arrays. The ``Dimension`` object,
which is also a key component of ``File`` class, provides an interface
to access dimensions.

.. note:: 

   ``Dimension`` instances should be created using the :meth:`File.def_dim` method of a ``File`` instance,
   not using :meth:`Dimension.__init__` directly.

.. autoclass:: pnetcdfpy::Dimension
   :members: getfile, isunlimited
   :exclude-members: name, size

Dimension Attributes
 The following class members are read-only and should not be modified by the user.

 .. attribute:: name

    String name of Dimension instance. This class member is read-only and
    should not be modified by the user. To rename a dimension, use :meth:`File.rename_dim` method.

 .. attribute:: size
      
    The current size of Dimension (calls ``len`` on Dimension instance). 