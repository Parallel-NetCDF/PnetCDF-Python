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
       :noindex:

    .. automethod:: close
       :noindex:

    .. automethod:: filepath
       :noindex:

    .. automethod:: sync
       :noindex:

    .. automethod:: redef
       :noindex:

    .. automethod:: enddef
       :noindex:

    .. automethod:: begin_indep
       :noindex:

    .. automethod:: end_indep
       :noindex:

    .. automethod:: flush
       :noindex:

    .. automethod:: def_dim
       :noindex:

    .. automethod:: rename_var
       :noindex:

    .. automethod:: rename_dim
       :noindex:

    .. automethod:: def_var
       :noindex:

    .. automethod:: ncattrs
       :noindex:

    .. automethod:: put_att
       :noindex:

    .. automethod:: get_att
       :noindex:

    .. automethod:: del_att
       :noindex:

    .. automethod:: rename_att
       :noindex:

    .. automethod:: wait
       :noindex:

    .. automethod:: wait_all
       :noindex:

    .. automethod:: cancel
       :noindex:

    .. automethod:: get_nreqs
       :noindex:

    .. automethod:: attach_buff
       :noindex:

    .. automethod:: detach_buff
       :noindex:

    .. automethod:: set_fill
       :noindex:

    .. automethod:: inq_buff_usage
       :noindex:

    .. automethod:: inq_buff_size
       :noindex:

    .. automethod:: inq_num_rec_vars
       :noindex:

    .. automethod:: inq_num_fix_vars
       :noindex:

    .. automethod:: inq_striping
       :noindex:

    .. automethod:: inq_recsize
       :noindex:

    .. automethod:: inq_version
       :noindex:

    .. automethod:: inq_info
       :noindex:

    .. automethod:: inq_header_size
       :noindex:

    .. automethod:: inq_put_size
       :noindex:

    .. automethod:: inq_header_extent
          :noindex:




.. attribute:: dimensions
    The dimensions dictionary maps the names of dimensions defined for the file 
    to instances of the `Dimension` class.

.. attribute:: variables
    The variables dictionary maps the names of variables defined for this file 
    to instances of the Variable class.


