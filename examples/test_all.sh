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
echo "OUT_DIR=$OUT_DIR"

TETS_PROGS="collective_write.py
            create_open.py
            fill_mode.py
            flexible_api.py
            get_info.py
            ghost_cell.py
            global_attribute.py
            hints.py
            nonblocking_write_def.py
            nonblocking_write.py
            put_varn_int.py
            transpose2D.py
            transpose.py
            put_vara.py
            get_vara.py"

for prog in $TETS_PROGS
do
   # echo -n "---- Testing $prog with $NPROC MPI processes"
   printf '%-60s' "Testing $prog with $NPROC MPI processes"

   if test $prog = "get_vara.py" ; then
      CMD="mpiexec -n $NPROC python $prog -q $OUT_DIR/put_vara.nc"
   else
      CMD="mpiexec -n $NPROC python $prog -q $OUT_DIR/${prog%.*}.nc"
   fi
   $CMD
   status=$?
   if [ $status -ne 0 ]; then
      echo " ---- FAIL"
   else
      echo " ---- PASS"
   fi
done

