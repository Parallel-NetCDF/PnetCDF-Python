=============================================
Compatibility with C
=============================================

The Following table contains list of PnetCDF-python's compatibility with PnetCDF-C APIs.

+----------------+-----------------------------+------------------------------------+
| | Component    | | Implemented               | | To be implemented (priority [1]_)|
+================+=============================+====================================+
| | File API     | | ncmpi_strerror            | | ncmpi_inq_libvers (3)            |
| |              | | ncmpi_strerrno            | | ncmpi_set_fill (3)               |
| |              | | ncmpi_create              | | ncmpi_set_default_format (3)     |
| |              | | ncmpi_open/close          | | ncmpi_inq_put/get_size (3)       |
| |              | | ncmpi_enddef/redef        | | ncmpi_delete (2)                 |
| |              | | ncmpi_sync                | | ncmpi_sync_numrecs (2)           |
| |              | | ncmpi_begin/end_indep_data| | ncmpi_inq_file_info (3)          |
| |              | | ncmpi_inq_path            | | ncmpi_inq_files_opened (3)       |
| |              | | ncmpi_inq                 | |                                  |
| |              | | ncmpi_wait                | |                                  |
| |              | | ncmpi_wait_all            | |                                  |
+----------------+-----------------------------+------------------------------------+
| | Dimension API| | ncmpi_def_dim             | |                                  |
| |              | | ncmpi_inq_ndims           | |                                  |
| |              | | ncmpi_inq_dimlen          | |                                  |
| |              | | ncmpi_inq_dim             | |                                  |
| |              | | ncmpi_inq_dimname         | |                                  |
+----------------+-----------------------------+------------------------------------+
| | Attribute API| | ncmpi_put/get_att_text    | |                                  |
| |              | | ncmpi_put/get_att         | |                                  |
| |              | | ncmpi_inq_att             | |                                  |
| |              | | ncmpi_inq_natts           | |                                  |
| |              | | ncmpi_inq_attname         | |                                  |
| |              | | ncmpi_rename_att          | |                                  |
| |              | | ncmpi_del_att             | |                                  |
+----------------+-----------------------------+------------------------------------+
| | Variable  API| | ncmpi_def_var             | | ncmpi_iput/iget_var1 (1)         |
| |              | | ncmpi_def_var_fill        | | ncmpi_iput/iget_vars (1)         |
| |              | | ncmpi_inq_varndims        | | ncmpi_iput/iget_varm (1)         |
| |              | | ncmpi_inq_varname         | | ncmpi_iput/iget_varn (2)         |
| |              | | ncmpi_put/get_vara        | | ncmpi_bput/bget_var (1)          |
| |              | | ncmpi_put/get_vars        | | ncmpi_bput/bget_var1 (1)         |
| |              | | ncmpi_put/get_var1        | | ncmpi_bput/bget_vara (1)         |
| |              | | ncmpi_put/get_var         | | ncmpi_bput/bget_vars (1)         |
| |              | | ncmpi_put/get_varn        | | ncmpi_bput/bget_varm (1)         |
| |              | | ncmpi_put/get_varm        | | ncmpi_bput/bget_varn (2)         |
| |              | | ncmpi_put/get_vara_all    | | ncmpi_wait/wait_all (1)          |
| |              | | ncmpi_put/get_vars_all    | | ncmpi_inq_nreqs (1)              |
| |              | | ncmpi_put/get_var1_all    | | ncmpi_inq_buffer_usage/size (1)  |
| |              | | ncmpi_put/get_var_all     | | ncmpi_cancel (1)                 |
| |              | | ncmpi_put/get_varn_all    | | ncmpi_fill_var_rec (2)           |
| |              | | ncmpi_put/get_varm_all    | |                                  |
| |              | | ncmpi_iput/iget_var       | |                                  |
| |              | | ncmpi_iput/iget_vara      | |                                  |
+----------------+-----------------------------+------------------------------------+

.. [1]  priority level 1/2/3 maps to first/second/third priority