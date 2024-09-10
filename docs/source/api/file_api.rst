================
Files
================

An instance of class ``pnetcdf.File`` is a high-level object representing a
netCDF file. The class methods provide a set of Pythonic interfaces to create,
read and write a netCDF file. A ``File`` instance serves as the root container
for dimensions, variables, and attributes.  Together they describe the meaning
of data and relations among data objects stored in a netCDF file.

.. autoclass:: pnetcdf::File
   :members: __init__, close, filepath, redef, enddef, begin_indep, end_indep,
    sync, flush, def_dim, rename_var, rename_dim, def_var, ncattrs, put_att,
    get_att, del_att, rename_att, wait, wait_all, cancel, attach_buff,
    detach_buff, set_fill, inq_buff_usage, inq_buff_size, inq_num_rec_vars,
    inq_num_fix_vars, inq_striping, inq_recsize, inq_version, inq_info,
    inq_header_size, inq_put_size, inq_header_extent, inq_nreqs
   :exclude-members: dimensions, variables, file_format, indep_mode, path

Read-only python fields of class :class:`pnetcdf.File`
 The following class fields are read-only and should not be modified by the
 user.

   .. attribute:: dimensions

      The dimensions dictionary maps the names of dimensions defined in this
      file as an instance of the :class:`pnetcdf.Dimension`.

      **Type:** `dict`

   .. attribute:: variables

      The variables dictionary maps the names of variables defined in this file
      as an instance of the :class:`pnetcdf.Variable`.

      **Type:** `dict`

   .. attribute:: file_format

      The file format of the netCDF file. Possible values are one of the
      following strings. "CLASSIC", "CDF2", "64BIT_OFFSET", "64BIT", "CDF5",
      "64BIT_DATA", "NETCDF4" and "BP".

      **Type:** `str`

