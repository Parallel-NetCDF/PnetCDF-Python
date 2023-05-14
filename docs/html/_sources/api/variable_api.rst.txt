=========
Variable
=========

Variable is a core component of a netCDF file representing an array
of data values organized along one or more dimensions, with associated
metadata in the form of attributes. The ``Variable`` object in the library
provides operations to read and write the data and metadata of a variable
within a netCDF file. Particularly, data mode operations have a flexible
interface, where reads and writes can be done through either explicit
function-call style methods or indexer-style (numpy-like) syntax.

.. autoclass:: pncpy::Variable
   :members:
