==============
Dimension
==============

Dimension defines the shape and structure of variables and stores 
coordinate data for multidimensional arrays. The ``Dimension`` object,
which is also a key component of ``File`` class, provides an interface
to create, access and manipulate dimensions.

.. note:: 

   ``Dimension`` instances should be created using the ``File.def_dim`` method of a ``File`` instance,
   not using `Dimension.__init__` directly.

.. autoclass:: pncpy::Dimension
   :exclude-members: __init__, _getname,  __repr__, __str__, __len__
