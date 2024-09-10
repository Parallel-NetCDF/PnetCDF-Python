.. PnetCDF Python documentation master file, created by
   sphinx-quickstart on Fri Apr  7 15:56:03 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PnetCDF-Python User Guide
============================

**Release:** |release|

PnetCDF-python is a Python interface to PnetCDF, a high-performance parallel
I/O library for accessing netCDF files.  This integration with Python allows
for easy manipulation, analysis, and visualization of netCDF data using the
rich ecosystem of Python's scientific computing libraries, making it a valuable
tool for python-based applications that require high-performance access to
netCDF files.

.. toctree::
   :maxdepth: 2
   :caption: Installation

   installation/install

.. toctree::
   :maxdepth: 2
   :caption: Tutorial

   tutorial/basic
   tutorial/datatypes
   tutorial/read_write
   tutorial/non_blocking
   tutorial/compare_netcdf4

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   api/file_api
   api/dimension_api
   api/variable_api
   api/attribute_api
   api/function_api

.. toctree::
   :maxdepth: 1
   :caption: Copyright

   copyright

.. #.. toctree::
.. #   :maxdepth: 2
.. #   :caption: Development

.. #   development/compatibility


.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
