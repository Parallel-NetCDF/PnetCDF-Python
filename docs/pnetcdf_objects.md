## Data objects in PnetCDF python programming model

PnetCDF python programming model consists of the following data objects.

| Component | Description |
| ---- | --- |
| **File** |`pnetcdf.File` is a high-level object representing a netCDF file, which provides an interface to create, read and write contents in an netCDF file. A File object contains dimensions, variables, and attributes. Together they describe the structures of data objects and relations among them. |
| **Attribute** | NetCDF attributes can be created, read, and modified using python dictionary-like syntax. A Pythonic interface for metadata operations is provided both in the `File` class (for global attributes) and the `Variable` class (for variable's attributes). |
| **Dimension** | Dimension defines the dimensional shape of variables. NetCDF variables are multidimensional arrays. The `Dimension` object, which is also a key component of `File` class, provides an interface to create, and modify dimensions. |
| **Variable** | Variable is a core component of a netCDF file representing a multi-dimensional array of data values. In addition to data types and dimensions, variables can be associated with attributes. The `Variable` object provides operations to read and write the data and metadata of a variable stored in a netCDF file. PnetCDF programming is divided into `define` and `data` modes. New data objects can only be created in the `define` mode. Reading and writings data objects are done in the `data` mode. Switching between the two modes can be done by explicitly calling function `enddef()` of a file object. |

