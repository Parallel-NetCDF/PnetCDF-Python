================
File
================

``pncpy.File`` is a high-level object representing an netCDF file,
which provides a Pythonic interface to create, read and write within
an netCDF file. A File object serves as the root container for dimensions,
variables, and attributes. Together they describe the meaning of data and
relations among data fields stored in a netCDF file.

.. autoclass:: pncpy::File

    .. automethod:: __init__

    .. automethod:: close

    .. automethod:: filepath

    .. automethod:: sync

    .. automethod:: redef

    .. automethod:: enddef

    .. automethod:: begin_indep

    .. automethod:: end_indep

    .. automethod:: flush

    .. automethod:: def_dim

    .. automethod:: rename_var

    .. automethod:: rename_dim

    .. automethod:: def_var

    .. automethod:: ncattrs

    .. automethod:: put_att

    .. automethod:: get_att

    .. automethod:: del_att

    .. automethod:: rename_att

    .. automethod:: wait

    .. automethod:: wait_all

    .. automethod:: cancel

    .. automethod:: get_nreqs

    .. automethod:: attach_buff

    .. automethod:: detach_buff

    .. automethod:: set_fill

    .. automethod:: inq_buff_usage

    .. automethod:: inq_buff_size

    .. automethod:: inq_num_rec_vars

    .. automethod:: inq_num_fix_vars

    .. automethod:: inq_striping

    .. automethod:: inq_recsize

    .. automethod:: inq_version

    .. automethod:: inq_info

    .. automethod:: inq_header_size

    .. automethod:: inq_put_size
      
    .. automethod:: inq_header_extent
   



.. attribute:: dimensions
    The dimensions dictionary maps the names of dimensions defined for the file 
    to instances of the `Dimension` class.

.. attribute:: variables
    The variables dictionary maps the names of variables defined for this file 
    to instances of the Variable class.


