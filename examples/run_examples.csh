#!/bin/csh

# set -e

set OUT_DIR = ""
# Set the argument to pass to the test programs
foreach arg ( $argv )
  set OUT_DIR = $arg
end

if ( "$OUT_DIR" != "" ) then
  # Create directories within OUT_DIR using make
  mkdir -p $OUT_DIR
  echo "Created output nc file directories in $OUT_DIR"
endif

# Run each example file with or without MPI, if any of them failed, exit
foreach exp_file (`ls *.py`)
    if ($exp_file != "get_vara.py") then
        echo "Running example programs with mpiexec (4 processes): $exp_file"
        mpiexec -n 4 python3 $exp_file -q "${OUT_DIR}/$exp_file:r.nc" 
        if ($status != 0) then
            exit 1
        else
            echo "PASS:  $exp_file Python  parallel run on 4 processes ---------------"
        endif
    endif
end

mpiexec -n 4 python3 get_vara.py -q "${OUT_DIR}/put_vara.nc" 
if ($status != 0) then
    exit 1
else 
    echo "PASS:  get_vara.py Python parallel run on 4 processes ---------------"
endif