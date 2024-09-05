.. currentmodule:: pnetcdf
==============================
Nonblocking Reads and Writes
==============================

Alternative to blocking read/writes, PnetCDF-python nonblocking APIs allow
users to first post multiple requests and later flush them altogether in order
to achieve a better performance. A common practice is writing (or reading)
subarrays to (from) multiple variables, e.g. one or more subarrays for each
variable defined in the NetCDF file.

Nonblocking Write
-------------------

 Write requests can be posted by the method call of :meth:`Variable.iput_var`.
 Same as :meth:`Variable.put_var`, the behavior of :meth:`Variable.iput_var`
 varies depending on the pattern of provided optional arguments - `index`,
 `start`, `count`, `stride`, and `imap` as shown below. Note that the method
 only posts the request, which is not committed until :meth:`File.wait`. The
 method call returns a request id that can be optionally passed to
 :meth:`File.wait` to select this request.

 - `data` - Request to write an entire variable
 - `data`, `index` - Request to write a single data value
 - `data`, `start`, `count` - Request to write an array of values
 - `data`, `start`, `count`, `stride` - Request to write a subarray of values
 - `data`, `start`, `count`, `imap` - Request to write a mapped array of values

 Here's a python example to post 10 write requests that write to 10 netCDF
 variables in the same file.

 .. code-block:: Python

    req_ids = []
    write_buff = [randint(0,10, size=(xdim,ydim,zdim)).astype('i4')] * 10

    for i in range(num_reqs):
        v = f.variables[f'data{i}']
        datam = write_buff[i]

        # post a request to write the whole variable
        req_id = v.iput_var(datam)
        # track the request ID for each write request
        req_ids.append(req_id)

    # wait for nonblocking writes to complete
    errs = [None] * num_reqs
    f.wait_all(num_reqs, req_ids, errs)

 For the full example program, see ``examples/nonblocking/nonblocking_write.py``.

Nonblocking Read
------------------

 Read requests can be posted by the method call of :meth:`Variable.iget_var`.
 Note that unlike :meth:`Variable.get_var`, this method requires a mandatory
 argument - an empty numpy array reserved to be filled in the future. Again,
 the method call returns a request id that can be optionally passed to
 :meth:`File.wait` to select this request. Similar to :meth:`Variable.get_var`,
 the behavior of :meth:`Variable.iget_var` varies depending on the pattern of
 provided optional arguments - `index`, `start`, `count`, `stride`, and `imap`.

 - `buff` - Request to read an entire variable
 - `buff`, `index` - Request to read a single data value
 - `buff`, `start`, `count` - Request to read an array of values
 - `buff`, `start`, `count`, `stride` - Request to read a subarray of values
 - `buff`, `start`, `count`, `imap` - Request to read a mapped array of values

 Here's a python example to post 10 read requests that read from 10 netCDF variables in the same file.

 .. code-block:: Python

    # initialize the list of references to read buffers
    v_datas = []

    req_ids = []
    for i in range(num_reqs):
        v = f.variables[f'data{i}']
        # allocate read buffer, a numpy array
        buff = np.empty(shape = v.shape, dtype = v.datatype)

        # post a request to read the whole variable
        req_id = v.iget_var(buff)
        # track the request ID for each read request
        req_ids.append(req_id)

        # store the reference of variable values
        v_datas.append(buff)

    # wait for nonblocking reads to complete
    errs = [None] * num_reqs
    f.wait_all(num_reqs, req_ids, errs)

 For the full example program, see ``examples/nonblocking/nonblocking_read.py``.

Commit Read/Write Requests
----------------------------

 Pending requests are eventually processed by :meth:`File.wait`. Requests to
 committed can be specified selectively specified by a request id list.  If so,
 optionally, user can pass in a empty list to collect error statuses of each
 request, which is useful in request-wise error tracking and debugging.
 Alternatively, user can flush all pending write and/or read requests using
 module-level NC constants (e.g. `NC_REQ_ALL`) as input parameters. The suffix
 `_all` indicates this is collective I/O in contrast to independent I/O
 (without `_all`).

 Here's a python example to commit selected requests:

 .. code-block:: Python

    # when the file is in the collective I/O mode
    req_errs = [None] * num_reqs
    f.wait_all(num_reqs, req_ids, req_errs)

    # when the file is in the independent I/O mode
    f.wait(num_reqs, req_ids, req_errs)

    # commit all pending write requests
    f.wait_all(num = NC_PUT_REQ_ALL)

    # commit all pending read requests
    f.wait_all(num = NC_GET_REQ_ALL)

Buffered Nonblocking Write
-----------------------------

 One limitation of the above nonblocking write is that users should not alter
 the contents of the write buffer once the request is posted until the wait API
 is returned.  Any change to the buffer contents in between will result in
 unexpected error. To alleviate the this limitation, use can post buffered
 nonblocking write requests using :meth:`Variable.bput_var`. The input
 parameters and returned values are identical to :meth:`Variable.iput_var`.
 However, user are free to alter/reuse/delete the write buffer once the
 requests is posted. As a prerequisite, the user need to tell PnetCDF the size
 of memory space required for all future requests to this netCDF file. This step
 is achieved by :meth:`File.attach_buff`.

 Here's a python example to post a number of write requests and commit them
 using buffered nonblocking API:

 .. code-block:: Python

    data = randint(0,10, size=(xdim,ydim,zdim)).astype('i4')

    write_buff = [data] * num_reqs
    # Estimate the memory buffer size of all write requests
    buffsize = num_reqs * data.nbytes

    # Attach buffer for buffered put requests
    f.attach_buff(buffsize)

    req_ids = []
    for i in range(num_reqs):
       v = f.variables[f'data{i}']
       # Post a request to write the whole variable
       req_id = v.bput_var(write_buff[i])
       # Track the request ID for each write request
       req_ids.append(req_id)

    # Users can now alter the contents of write_buff here

    # wait for nonblocking, buffered writes to complete
    f.wait_all()

    # Tell PnetCDF to detach the internal buffer
    f.detach_buff()

 For the full example program, see ``examples/nonblocking/nonblocking_write.py``.

 Remember to detach the write buffer to free up the memory space.


