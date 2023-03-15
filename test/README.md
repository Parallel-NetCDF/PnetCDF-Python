# Pnetcdf-python unittest
## Setup
* Make sure you are in top-level directory
* Make sure Pnetcdf-python is installed by running `env CC=mpicc python3 setup.py build` 

## Launch single test 
### Run a specific test program with single process
```sh
python3 test/test_progrm.py
```
### Specify generated test directory to preserve test nc files (auto-deleted in default)
```sh
python3 test/test_progrm.py [testfile-dir]
```
### Run a specific test program with MPI (multi-processing) 
```sh
mpiexec -n [number of process] python3 test/test_progrm.py
```

## Automatically run all 
### Run all test programs with optional mpi flag & optional testfile dir

```sh
test_all.csh [--mpi] [testfile-dir]
```