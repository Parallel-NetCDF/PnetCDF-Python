#!/bin/csh

# set -e
# Get the directory containing this script
set SCRIPT_DIR=`dirname $0`

# Change into the test directory
cd $SCRIPT_DIR/test

# Determine whether MPI testing is enabled
set MPI_EXE = false
set OUT_DIR = ""
# Set the argument to pass to the test programs
foreach arg ( $argv )
  if ( "$arg" == "--mpi" ) then
    set MPI_EXE = true
  else
    set OUT_DIR = $arg
  endif
end


# Run each test file with or without MPI
foreach test_file (`ls tst_*.py`)
  if ( $MPI_EXE == true ) then
    echo "Running unittest program with mpiexec (4 processes): $test_file"
    mpiexec -n 4 python3 $test_file $OUT_DIR 
  else
    echo "Running unittest program: $test_file"
    
    python3 $test_file $OUT_DIR 
  endif
end
