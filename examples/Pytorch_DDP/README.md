# Example Python programs that use Pytorch Distributed Data Parallel module

This directory contains example python programs that make use of Pytorch
Distributed Data Parallel (DDP) module and MPI to run on multiple MPI processes
in parallel. Detailed information describing the example programs is provided
at the beginning of each file.

## [torch_ddp_skeleton.py](./torch_ddp_skeleton.py) shows how to set up the MPI
and DDP environment to run a program in parallel.

Command usage:
```sh
% mpiexec -n 4 python ./torch_ddp_skeleton.py 
nprocs =  4  rank =  0  device =  cpu
nprocs =  4  rank =  1  device =  cpu
nprocs =  4  rank =  2  device =  cpu
nprocs =  4  rank =  3  device =  cpu
```


