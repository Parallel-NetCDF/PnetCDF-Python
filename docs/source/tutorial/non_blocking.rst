==============================
Non-blocking Reads and Writes
==============================

.. warning::

   Under construction. 

 
 
Alternative to blocking read/writes, PnetCDF nonblocking APIs allow users to first post multiple requests and later flush them altogether 
in order to achieve a better performance. A common practice is writing (or reading) subarrays to (from) multiple variables, e.g. one or more
subarrays for each variable defined in the NetCDF file.

Nonblocking Write
--------------------------------------

 Write requests can be posted by the method call of :func:`Variable.iput_var()`. Same as :func:`Variable.put_var()`, the behavior of :func:`Variable.iput_var()` varies 
 depending on the pattern of provided optional arguments - `index`, `start`, `count`, `stride`, `num` and `imap` as shown below. Note that the method only posts the 
 request, which is not commited until :func:`File.wait()`. The method call returns a request id that can be optionally passed to :func:`File.wait()` to select this request.

 - `data` - Reqeust to write an entire variable
 - `data`, `index` - Reqeust to write a single data value
 - `data`, `start`, `count` - Reqeust to write an array of values
 - `data`, `start`, `count`, `stride` - Reqeust to write a subsampled array of values
 - `data`, `start`, `count`, `imap` - Reqeust to write a mapped array of values
 - `start`, `count`, `num` - Reqeust to write a list of subarrays of values
 
 Here's a python example to post 10 write requests that write to 10 netCDF variables in the same file. 

 .. code-block:: Python

    req_ids = []
    write_buff = [randint(0,10, size=(xdim,ydim,zdim)).astype('i4')] * 10
    for i in range(num_reqs):
      v = f.variables[f'data{i}']
      datam = write_buff[i]
      # post the request to write the whole variable
      req_id = v.iput_var(datam)
      # track the request ID for each write request
      req_ids.append(req_id)

 For more, see `examples/non_blocking_write.py`.

Nonblocking Read
--------------------------------------

 Read requests can be posted by the method call of :func:`Variable.iget_var()`. Note that unlike :func:`Variable.get_var()`, this method requires a 
 mandatory argument - an empty numpy array reserved to be filled in the future. Again, the method call returns a request id that can be optionally passed to 
 :func:`File.wait()` to select this request. Similar to :func:`Variable.get_var()`, the behavior of :func:`Variable.iget_var()` varies depending on 
 the pattern of provided optional arguments - `index`, `start`, `count`, `stride`, `num` and `imap`. 

 - `buff` - Request to read an entire variable
 - `buff`, `index` - Request to read a single data value
 - `buff`, `start`, `count` - Request to read an array of values
 - `buff`, `start`, `count`, `stride` - Request to read a subsampled array of values
 - `buff`, `start`, `count`, `imap` - Request to read a mapped array of values
 - `buff`, `start`, `count`, `num` - Request to read a list of subarrays of a netCDF variable
 
 Here's a python example to post 10 read requests that read from 10 netCDF variables in the same file. 

 .. code-block:: Python

    req_ids = []
    # initialize the list of returned array references
    v_datas = []
    for i in range(num_reqs):       
       v = f.variables[f'data{i}']
       buff = np.empty(shape = v.shape, dtype = v.datatype)# empty numpy array to hold returned variable values
       req_id = v.iget_var(buff)
       # track the request ID for each read request
       req_ids.append(req_id)
       # store the reference of variable values
       v_datas.append(buff)
 
 For more, see `examples/flexible_api.py`.

Commit Read/Write Requests
--------------------------------------

 Pending requests are eventually processed by :func:`File.wait()`. Requests to commited can be specified selectively specified by a request id list. 
 If so, optionally, user can pass in a empty list to collect error statuses of each request, which is useful in request-wise error tracking and debugging.
 Alternatively, user can flush all pending write and/or read requests using module-level NC constants (e.g. `pncpy.NC_REQ_ALL`) as input parameters. The suffix
 `_all` indicates this is collective I/O in contrast to indepedent I/O (without `_all`).

 Here's a python example to commit selected requests:

 .. code-block:: Python

    # collective i/o 
    req_errs = [None] * num_reqs
    f.wait_all(num_reqs, req_ids, req_errs)
    # f.wait() # independent i/o
    # f.wait_all() # commit all requests
    # f.wait_all(num = pncpy.NC_PUT_REQ_ALL) # commit all write requests
    # f.wait_all(num = pncpy.NC_GET_REQ_ALL) # commit all read requests

Buffered Non-blocking Write
--------------------------------------

 One limitation of the above non-blocking write is that users should not alter the contents of the write buffer once the request is posted until the wait API is returned. 
 Any change to the buffer contents in between will result in unexpected error. To alleviate the this limitation, use can post buffered nonblocking write requests using 
 :func:`Variable.bput_var()`. The input parameters and returned values are identical to :func:`Variable.iput_var()`. However, user are free to alter/reuse/delete the write 
 buffer once the requests is postsed. As a prerequisite, the user need to tell PnetCDF the size of memory space required for all future reqests to this netCDF file. This step
 is achieved by :func:`File.attach_buff()`. 

 Here's a python example to post a number of write requests and commit them using buffered non-blocking API:
 
 .. code-block:: Python

    f.enddef()
    data = randint(0,10, size=(xdim,ydim,zdim)).astype('i4')
    write_buff = [data] * num_reqs
    # Estimate the memory buffer size of all write requests
    buffsize = num_reqs * data.nbytes
    # Attach buffer for buffered put requests
    f.attach_buff(buffsize)
    req_ids = []
    for i in range(num_reqs):
       v = f.variables[f'data{i}']
       # Post the request to write the whole variable
       req_id = v.bput_var(write_buff[i])
       # Track the request ID for each write request
       req_ids.append(req_id)
   # Free to alter the contents of write_buff here enabled by buffered non-blocking
    f.wait_all()
    f.detach_buff()
 
 For more, see `examples/non_blocking_write.py`.

 Remember to detach the write buffer after write requets are executed.
 
 
