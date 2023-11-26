#!/bin/csh

# Get the directory containing this script
if (! $?NPROC) then
    setenv NPROC 4
endif
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
  echo "Running unittest program with mpiexec ($NPROC processes): $test_file"
  mpiexec -n $NPROC python3 $test_file $OUT_DIR
  # if (issetenv PNETCDF_DIR) then
  #   env PNETCDF_DIR=$PNETCDF_DIR mpiexec -n 4 python3 $test_file $OUT_DIR 
  # else
  #   mpiexec -n 4 python3 $test_file $OUT_DIR
  # endif
  if ($status != 0) then
    exit 1
endif
end
