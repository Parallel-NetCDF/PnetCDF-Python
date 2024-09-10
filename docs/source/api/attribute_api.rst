===========
Attributes
===========

In `object-oriented programming <https://en.wikipedia.org/wiki/Object-oriented_programming>`_,
a class contains fields (state variables containing data) and methods
(subroutines or procedures defining the object's behavior in code). ``Fields``
may also be known as members, attributes, or properties. To avoid confusion
with NetCDF's terminology of ``attribute``, this document uses `field` to refer
to a class's state variable.

NetCDF attributes are small, supplementary metadata that annotates variables or
files.  NetCDF attribute is not a Python class by itself. Instead, it is a
field of python dictionary in class :class:`pnetcdf.File` and class
:class:`pnetcdf.Variable`.  Their data types can be any allowed by the classic
NetCDF file formats.  The most common data type is `text` for annotation
purpose.  NetCDF attributes can be created, accessed, and manipulated using
python dictionary-like syntax.  An attribute can be associated to a file,
referred to as ``golbal attribute``, as well as to individual variables,
referred to as ``variable's attribute``.  Pythonic interfaces for accessing
attributes are is provided both in class :class:`pnetcdf.File` (for global
attributes) and class :class:`pnetcdf.Variable` (for variable attributes).
Example programs are `examples/global_attribute.py` and `examples/put_var.py`.

