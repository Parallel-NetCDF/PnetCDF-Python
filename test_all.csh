#!/bin/csh

# set -e
# Get the directory containing this script
set SCRIPT_DIR=`dirname $0`

# Change into the test directory
cd $SCRIPT_DIR/test


set OUT_DIR = ""
# Set the argument to pass to the test programs
foreach arg ( $argv )
  set OUT_DIR = $arg
end


# Run each test file with or without MPI
foreach test_file (`ls tst_*.py`)
  echo "Running unittest program with mpiexec (4 processes): $test_file"
  mpiexec -n 4 python3 $test_file $OUT_DIR 
  if ($status != 0) then
    exit 1
endif
end
