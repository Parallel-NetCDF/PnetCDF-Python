===========
Attributes
===========

NetCDF attributes can be created, accessed, and manipulated using python
dictionary-like syntax. An attribute can be associated to the file, referred to
as ``golbal attribute``, as well as to individual variable, referred to as
``variable's attribute``. Pythonic interfaces for accessing attributes are is
provided both in :class:`pnetcdf.File` (for global attributes) and the
:class:`pnetcdf.Variable` (for variable attributes).

