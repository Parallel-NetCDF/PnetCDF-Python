# PnetCDF-python - Current development status

PnetCDF-python development is an on-going project. The implementation of
its feature is added gradually. While most of its APIs corresponding to
its C counterparts have been implemented, there are still some left to be
implemented. Tables below show the status of the APIs.

<!-- * **Implemented:** netCDF file operations API, dimension operations API, attribute operations API, variable define mode operations
* **Partially implemented:** variable blocking mode data operations (90% completed)
* **Planned:** variable non-blocking mode data operations -->
| Component | Implemented | To be implemented next (w/ priority\*) |
| ---- | --- | --- |
|File API| ncmpi_strerror<br />ncmpi_strerrno<br />ncmpi_create<br />ncmpi_open/close<br />ncmpi_enddef/redef<br />ncmpi_sync<br />ncmpi_begin/end_indep_data<br />ncmpi_inq_path <br />ncmpi_inq<br />ncmpi_wait<br />ncmpi_wait_all<br />ncmpi_inq_nreqs <br />ncmpi_inq_buffer_usage/size <br />ncmpi_cancel <br />ncmpi_set_fill <br />ncmpi_set_default_format <br />ncmpi_inq_file_info<br />ncmpi_inq_put/get_size <br />ncmpi_inq_files_opened<br />|  ncmpi_inq_libvers<sup>2</sup><br /> ncmpi_delete<sup>2</sup><br /> ncmpi_sync_numrecs<sup>2</sup><br /> ncmpi__enddef<sup>2</sup><br />  ncmpi_abort<sup>3</sup><br />|
|Dimension API|ncmpi_def_dim<br />ncmpi_inq_ndims<br />ncmpi_inq_dimlen<br />ncmpi_inq_dim<br />ncmpi_inq_dimname<br />ncmpi_rename_dim<br />| |
|Attribute API| ncmpi_put/get_att_text<br />ncmpi_put/get_att<br />ncmpi_inq_att<br />ncmpi_inq_natts<br />ncmpi_inq_attname<br />ncmpi_rename_att<br />ncmpi_del_att|ncmpi_copy_att<sup>2</sup><br />|
|Variable API| ncmpi_def_var<br />ncmpi_def_var_fill<br />ncmpi_inq_varndims<br />ncmpi_inq_varname<br />ncmpi_put/get_vara<br />ncmpi_put/get_vars<br />ncmpi_put/get_var1<br />ncmpi_put/get_var<br />ncmpi_put/get_varn<br />ncmpi_put/get_varm<br /> ncmpi_put/get_vara_all<br />ncmpi_put/get_vars_all<br />ncmpi_put/get_var1_all<br />ncmpi_put/get_var_all<br />ncmpi_put/get_varn_all<br />ncmpi_put/get_varm_all<br />ncmpi_iput/iget_var<br />ncmpi_iput/iget_vara<br />ncmpi_iput/iget_var1<br />ncmpi_iput/iget_vars<br />ncmpi_iput/iget_varm<br /> ncmpi_iput/iget_varn<br /> ncmpi_bput_var<br />ncmpi_bput_var1<br />ncmpi_bput_vara<br />ncmpi_bput_vars<br />ncmpi_bput_varm<br />ncmpi_bput_varn<br />ncmpi_fill_var_rec<br />|All type-specific put/get functions<sup>3</sup> <br /> (e.g. ncmpi_put_var1_double_all)<br /><br />All put/get_vard functions<sup>3</sup><br /><br />All mput/mget_var functions<sup>3</sup>|
|Inquiry API|ncmpi_inq<br />ncmpi_inq_ndims<br />ncmpi_inq_dimname<br />ncmpi_inq_varnatts<br />ncmpi_inq_nvars<br />ncmpi_inq_vardimid<br />ncmpi_inq_var_fill<br />ncmpi_inq_buffer_usage<br />ncmpi_inq_buffer_size<br />ncmpi_inq_natts<br /> ncmpi_inq_malloc_max_size<br />ncmpi_inq_malloc_size<br />ncmpi_inq_format <br />ncmpi_inq_file_format<br />ncmpi_inq_num_rec_vars<br />ncmpi_inq_num_fix_vars<br />ncmpi_inq_unlimdim<br />ncmpi_inq_varnatts<br />ncmpi_inq_varndims<br />ncmpi_inq_varname<br />ncmpi_inq_vartype<br />ncmpi_inq_varoffset<br />ncmpi_inq_header_size<br />ncmpi_inq_header_extent<br />ncmpi_inq_recsize <br />ncmpi_inq_version<br />ncmpi_inq_striping<br />|ncmpi_inq_dimid<sup>3</sup><br />ncmpi_inq_dim<sup>3</sup><br />ncmpi_inq_malloc_list<sup>2</sup><br /> ncmpi_inq_var<sup>3</sup><br /> ncmpi_inq_varid<sup>3</sup><br />|

priority level 1/2/3 maps to first/second/third priority.



