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

MPI4PY_VERSION=`python -c "import mpi4py; print(mpi4py.__version__)"`
MPI4PY_VERSION_MAJOR=`echo ${MPI4PY_VERSION} | cut -d. -f1`
# echo "MPI4PY_VERSION=$MPI4PY_VERSION"
# echo "MPI4PY_VERSION_MAJOR=$MPI4PY_VERSION_MAJOR"

TEST_FLEXIBLE_API=no
if test "x$PNETCDF_DIR" != x ; then
   PNETCDF_C_VERSION=`$PNETCDF_DIR/bin/pnetcdf-config --version | cut -d' ' -f2`
   V_MAJOR=`echo ${PNETCDF_C_VERSION} | cut -d. -f1`
   V_MINOR=`echo ${PNETCDF_C_VERSION} | cut -d. -f2`
   V_SUB=`echo ${PNETCDF_C_VERSION} | cut -d. -f3`
   VER_NUM=$((V_MAJOR*1000000 + V_MINOR*1000 + V_SUB))
   if test $VER_NUM -gt 1013000 ; then
      TEST_FLEXIBLE_API=yes
   fi
fi

# test PnetCDF flexible APIs only when PnetCDF-C >= 1.13.1 or mpi4py < 4
if test $MPI4PY_VERSION_MAJOR -lt 4 ; then
   TEST_FLEXIBLE_API=yes
fi

for prog in $check_PROGRAMS; do
   if test "x$TEST_FLEXIBLE_API" = xno &&
      test "x$prog" = "xflexible_api.py" ; then
      TETS_PROGS+=" flexible_api.py"
      printf '%-60s' "Testing $prog"
      echo " ---- SKIP"
      continue
   fi

   printf '%-60s' "Testing $prog"

   CMD="mpiexec -n $NPROC python $prog -q $OUT_DIR/${prog%.*}.nc"
   $CMD
   status=$?
   if [ $status -ne 0 ]; then
      echo " ---- FAIL"
   else
      echo " ---- PASS"
   fi
done

