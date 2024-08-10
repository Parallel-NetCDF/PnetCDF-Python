# PnetCDF-python MNIST example

This directory contains the description and run instructions for the MNIST example Python programs that utilize PnetCDF for file I/O and parallel training with MNIST data.

## Directory Structure

- **MNIST_data**: This folder contains a mini MNIST test dataset stored in a NetCDF file (`mnist_images_mini.nc`). The file includes:
  - 60 training samples
  - 12 testing samples

- **MNIST_codes**: This folder contains the example MNIST training code. The example code is based on the [PyTorch MNIST example](https://github.com/pytorch/examples/tree/main/mnist) and uses `DistributedDataParallel` for parallel training.

## Running the MNIST Example Program

To run the MNIST example program, use the `mpiexec` command. The example below runs the program on 4 MPI processes.

### Command:

```sh
mpiexec -n 4 python main.py
```

### Expected Output:

When using 4 MPI processes, the output is expected to be similar to the following:

```sh
nprocs = 4  rank = 0  device = cpu  mpi_size = 4  mpi_rank = 0
nprocs = 4  rank = 2  device = cpu  mpi_size = 4  mpi_rank = 2
nprocs = 4  rank = 1  device = cpu  mpi_size = 4  mpi_rank = 1
nprocs = 4  rank = 3  device = cpu  mpi_size = 4  mpi_rank = 3

Train Epoch: 1  Average Loss: 2.288340
Test set: Average loss: 2.7425, Accuracy: 0/12 (0%)

Train Epoch: 2  Average Loss: 2.490800
Test set: Average loss: 1.9361, Accuracy: 6/12 (50%)

Train Epoch: 3  Average Loss: 2.216520
Test set: Average loss: 1.8703, Accuracy: 7/12 (58%)
```

### Notes:
- The test set accuracy may vary slightly depending on how the data is distributed across the MPI processes.
- The accuracy and loss reported after each epoch are averaged across all MPI processes.

