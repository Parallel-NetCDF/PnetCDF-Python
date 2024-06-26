## Programming difference between NetCDF4-python and PnetCDF-python
* Table below shows examples of source code.
  + Both example codes write to a variable named `WIND` in the collective mode.
  + The differences are marked in colors, green for NetCDF and blue for PnetCDF.

| NetCDF4 | PnetCDF |
|:-------|:--------|
|  # create a new file   | |
| ${\textsf{\color{green}f = netCDF4.Dataset}}$(filename="testfile.nc", mode="w", comm=comm, parallel=True)  | ${\textsf{\color{blue}f = pncpy.File}}$(filename="testfile.nc", mode='w', comm=comm) |
|  # add a global attributes   | |
| ${\textsf{\color{green}f.history = }}$"Wed Mar 27 14:35:25 CDT 2024"  | ${\textsf{\color{blue}f.history = }}$"Wed Mar 27 14:35:25 CDT 2024"   |
|  # define dimensions   | |
| ${\textsf{\color{green}lat\\_dim = f.createDimension}}$("lat", 360)  | ${\textsf{\color{blue}lat\\_dim = f.def\\_dim}}$("lat", 360)  |
| ${\textsf{\color{green}lon\\_dim = f.createDimension}}$("lon", 720)  | ${\textsf{\color{blue}lon\\_dim = f.def\\_dim}}$("lon", 720)  |
| ${\textsf{\color{green}time\\_dim = f.createDimension}}$("time", None)  | ${\textsf{\color{blue}time\\_dim = f.def\\_dim}}$("time", -1)  |
|  # define a 3D variable of float type   | |
| ${\textsf{\color{green}var = f.createVariable}}$(varname="WIND", datatype="f8", dimensions = ("time", "lat", "lon"))  | ${\textsf{\color{green}var = f.def\\_var}}$(varname="WIND", nc\_type=pncpy.NC\_FLOAT, dimensions = ("time", "lat", "lon"))  |
|  # add attributes to the variable   | |
| ${\textsf{\color{green}var.long\\_name}}$="atmospheric wind velocity magnitude"  |${\textsf{\color{blue}var.long\\_name}}$="atmospheric wind velocity magnitude"  |
| ${\textsf{\color{green}var.setncattr}}$("int_att", np.int32(1))|${\textsf{\color{blue}var.put\\_att}}$("int_att", np.int32(1))  |
|  # exit define mode   | |
| # No code needed. netCDF4-python automatically switches data and define mode | ${\textsf{\color{blue}f.enddef()}}$ | |
|  # collectively write to variable WIND   | |
| buff = np.zeros(shape = (5, 10), dtype = "f8") | |
| ${\textsf{\color{green}var[0, 5:10, 0:10]}}$ = buff  | ${\textsf{\color{blue}var[0, 5:10, 0:10]}}$ = buff  |
| | # alternatively <br> ${\textsf{\color{blue}var.put\\_var\\_all}}$(buff, start = [0, 5, 0], count = [1, 5, 10]) |
|  # close file   | |
| ${\textsf{\color{green}f.close()}}$ | ${\textsf{\color{blue}f.close()}}$  |
