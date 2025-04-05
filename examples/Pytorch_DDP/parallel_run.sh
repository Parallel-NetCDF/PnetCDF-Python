#!/bin/bash
#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

# Exit immediately if a command exits with a non-zero status.
set -e

# Get the directory containing this script
if test "x$NPROC" = x ; then
    NPROC=4
fi

# get output folder from command line
if test "$#" -gt 0 ; then
   args=("$@")
   OUT_DIR="${args[0]}"
   # check if output folder exists
   if ! test -d $OUT_DIR ; then
      echo "Error: output folder \"$OUT_DIR\" does not exist."
      exit 1
   fi
else
   # output folder is not set at command line, use current folder
   OUT_DIR="."
fi
# echo "OUT_DIR=$OUT_DIR"

for prog in $check_PROGRAMS; do
   printf '%-60s' "Testing $prog"

   if test $prog = "torch_ddp_skeleton.py" ; then
      CMD="${TESTMPIRUN} -n $NPROC python $prog -q"
   fi
   $CMD
   status=$?
   if [ $status -ne 0 ]; then
      echo " ---- FAIL"
   else
      echo " ---- PASS"
   fi
done

