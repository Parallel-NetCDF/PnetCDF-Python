================
File
================

``pncpy.File`` is a high-level object representing an netCDF file,
which provides a Pythonic interface to create, read and write within
an netCDF file. A File object serves as the root container for dimensions,
variables, and attributes. Together they describe the meaning of data and
relations among data fields stored in a netCDF file.

.. autoclass:: pncpy::File
   :members: 
   :undoc-members:

   .. attribute:: dimensions

    The dimensions dictionary maps the names of dimensions defined for the file 
    to instances of the `Dimension` class.

   .. attribute:: variables

    The variables dictionary maps the names of variables defined for this file 
    to instances of the Variable class.


