#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

check:
	cd test && make check
	cd examples && make check

ptests:
	cd test && make ptests
	cd examples && make ptests

clean:
	cd test && make clean
	cd examples && make clean

build-clean: clean
	rm -rf build
	rm -rf src/pnetcdf.egg-info/
	rm -rf src/pnetcdf/_Dimension.c
	rm -rf src/pnetcdf/_Dimension.*.so
	rm -rf src/pnetcdf/_File.c
	rm -rf src/pnetcdf/_File.*.so
	rm -rf src/pnetcdf/_Variable.c
	rm -rf src/pnetcdf/_Variable.*.so
	rm -rf src/pnetcdf/_utils.c
	rm -rf src/pnetcdf/_utils.*.so
	rm -rf src/pnetcdf/__pycache__/
	rm -rf test/__pycache__/

install-clean: build-clean
	rm -rf dist

