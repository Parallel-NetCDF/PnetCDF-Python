================
File
================

``pncpy.File`` is a high-level object representing an netCDF file,
which provides a Pythonic interface to create, read and write within
an netCDF file. A File object serves as the root container for dimensions,
variables, and attributes. Together they describe the meaning of data and
relations among data fields stored in a netCDF file.

.. autoclass:: pncpy::File
   :members: __init__, close, filepath, redef, enddef, begin_indep, end_indep,
    sync, flush, def_dim, rename_var, rename_dim, def_var, ncattrs, put_att, get_att,
    del_att, rename_att, wait, wait_all, cancel, attach_buff, detach_buff, set_fill,
    inq_buff_usage, inq_buff_size, inq_num_rec_vars, inq_num_fix_vars, inq_striping,
    inq_recsize, inq_version, inq_info, inq_header_size, inq_put_size, inq_header_extent,
    inq_nreqs
   :exclude-members: indep_mode, path

.. rubric:: Attributes

.. attribute:: dimensions

    The dimensions dictionary maps the names of dimensions defined for the file 
    to instances of the ``Dimension`` class. This class member is read-only and
    should not be modified by the user.

.. attribute:: variables
      
    The variables dictionary maps the names of variables defined for this file 
    to instances of the ``Variable`` class. This class member is read-only and
    should not be modified by the user.

.. attribute:: file_format
    
    The file format in string of the netCDF file. Possible values include: "CLASSIC", "CDF2",
    "64BIT_OFFSET", "64BIT", "CDF5", "64BIT_DATA", "NETCDF4" and "BP". This class member is 
    read-only and should not be modified by the user.

    



