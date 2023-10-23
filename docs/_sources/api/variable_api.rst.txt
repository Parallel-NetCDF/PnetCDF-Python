=========
Variable
=========

Variable is a core component of a netCDF file representing an array
of data values organized along one or more dimensions, with associated
metadata in the form of attributes. The ``Variable`` object in the library
provides operations to read and write the data and metadata of a variable
within a netCDF file. Particularly, data mode operations have a flexible
interface, where reads and writes can be done through either explicit
function-call style methods or indexer-style (numpy-like) syntax.

.. autoclass:: pncpy::Variable
   :members: ncattrs, put_att, get_att, del_att, rename_att, get_dims, def_fill,
    inq_fill, fill_rec, set_auto_chartostring, set_auto_scale, set_auto_mask, 
    set_auto_maskandscale, put_var, put_var_all, get_var, get_var_all, iput_var, bput_var
    iget_var, inq_offset
   :exclude-members: name, shape, size



Variable Attributes
 The following class members are read-only and should not be modified by the user.

 .. attribute:: name

   The string name of Variable instance
   **Type:** `str`

 .. attribute:: dtype


   Return the mapped numpy data type of the variable netCDF datatype. A numpy dtype object 
   describing the variable's data type.
   **Type:** ``numpy.dtype``

 .. attribute:: datatype


   Same as ``Variable.dtype``.
   **Type:** ``numpy.dtype``

 .. attribute:: shape


   Return the shape of the variable, which is the current sizes of all variable 
   dimensions
   **Type:** `Tuple[int, int]`

 .. attribute:: ndim


   The number of variable dimensions.
   **Type:** `int`

 .. attribute:: size


   Return the number of stored elements
   **Type:** `int`

 .. attribute:: dimensions


   Return the variable's dimension names
   **Type:** `List[str]`

 .. attribute:: scale

   Only relevant when using indexer syntax to read from or write to netCDF variable. 
   If True, `scale_factor` and `add_offset` are applied, and signed integer data is 
   automatically converted to unsigned integer data if the `_Unsigned` attribute is set.
   Default is `True`, can be reset using `Variable.set_auto_scale` and
   `Variable.set_auto_maskandscale` methods.
   **Type:** `bool`

 .. attribute:: mask

   Only relevant when using indexer syntax to read from netCDF variable. If `True`, 
   data is automatically converted to/from masked arrays when missing values or fill 
   values are present. Default is `True`, can be reset using ``Variable.set_auto_mask`` 
   and ``Variable.set_auto_maskandscale`` methods. 
   **Type:** `bool`

 .. attribute:: chartostring


   If `True`, data is automatically converted to/from character
   arrays to string arrays when the `_Encoding` variable attribute is set.
   Default is `True`, can be reset using ``Variable.set_auto_chartostring`` method.
   **Type:** `bool`

