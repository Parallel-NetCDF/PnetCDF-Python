# MNIST example using PnetCDF-Python to Read Input Data

This directory contains files for running the Pytorch example program,
[MNIST](https://github.com/pytorch/examples/tree/main/mnist),
using Pytorch module `DistributedDataParallel` for parallel training and
`PnetCDF-Python` for reading data from a NetCDF files.

## Running the MNIST Example Program

* Firstly, run command below to generate the python program file.
  ```sh
  make mnist_main.py
  ```
* Run command below to train the model using 4 MPI processes.
  ```sh
  mpiexec -n 4 python mnist_main.py --batch-size 4 --test-batch-size 2 --epochs 3 --input-file mnist_images.nc
  ```

* `mnist_main.py` command-line options
  ```
  -h, --help            show this help message and exit
  --batch-size N        input batch size for training (default: 64)
  --test-batch-size N   input batch size for testing (default: 1000)
  --epochs N            number of epochs to train (default: 14)
  --lr LR               learning rate (default: 1.0)
  --gamma M             Learning rate step gamma (default: 0.7)
  --no-cuda             disables CUDA training
  --no-mps              disables macOS GPU training
  --dry-run             quickly check a single pass
  --seed S              random seed (default: 1)
  --log-interval N      how many batches to wait before logging training status
  --save-model          For Saving the current Model
  --input-file INPUT_FILE
                        NetCDF file storing train and test samples
  ```

## Testing
* Command `make check` will do the following.
  + Downloads the python source codes
    [main.py](https://github.com/pytorch/examples/blob/main/mnist/main.py)
    from [Pytorch Examples](https://github.com/pytorch/examples) as file
    `mnist_main.py`.
  + Applies patch file [mnist.patch](./mnist.patch) to `mnist_main.py`.
  + Run the training program `mnist_main.py` in parallel using 4 MPI processes.

* Testing output shown on screen.
  ```
  =====================================================================
      examples/MNIST: Parallel testing on 4 MPI processes
  ======================================================================
  Train Epoch: 1 [0/60 (0%)]	Loss: 2.514259
  Train Epoch: 1 [10/60 (67%)]	Loss: 1.953820

  Test set: Average loss: 2.2113, Accuracy: 4/12 (33%)

  Train Epoch: 2 [0/60 (0%)]	Loss: 2.359334
  Train Epoch: 2 [10/60 (67%)]	Loss: 2.092178

  Test set: Average loss: 1.4825, Accuracy: 6/12 (50%)

  Train Epoch: 3 [0/60 (0%)]	Loss: 2.067438
  Train Epoch: 3 [10/60 (67%)]	Loss: 0.010670

  Test set: Average loss: 1.2531, Accuracy: 7/12 (58%)
  ```

## Generate the Input NetCDF File From MNIST Datasets
* Utility program [create_mnist_netcdf.py](./create_mnist_netcdf.py)
  can be used to extract a subset of images into a NetCDF file.
* Command `make mnist_images.nc` will first download the MNIST data files from
  https://yann.lecun.com/exdb/mnist and extract 60 images as training samples
  and 12 images as testing samples into a new file named `mnist_images.nc`.
* `create_mnist_netcdf.py` can also run individually to extract a different
  number of images using command-line options shown below.
* `create_mnist_netcdf.py` command-line options:
  ```
    -h, --help            show this help message and exit
    --verbose             Verbose mode
    --train-size N        Number of training samples extracted from the input file (default: 60)
    --test-size N         Number of testing samples extracted from the input file (default: 12)
    --train-data-file TRAIN_DATA_FILE
                          (Optional) input file name of training data
    --train-label-file TRAIN_LABEL_FILE
                          (Optional) input file name of training labels
    --test-data-file TEST_DATA_FILE
                          (Optional) input file name of testing data
    --test-label-file TEST_LABEL_FILE
                          (Optional) input file name of testing labels
    --out-file OUT_FILE   (Optional) output NetCDF file name
  ```
* The NetCDF file metadata can be obtained by running command "ncmpidump -h" or
  "ncdump -h".
  ```sh
  % ncmpidump -h mnist_images.nc
  netcdf mnist_images {
  // file format: CDF-5 (big variables)
  dimensions:
	  height = 28 ;
	  width = 28 ;
	  train_num = 60 ;
	  test_num = 12 ;
  variables:
	  ubyte train_samples(train_num, height, width) ;
		  train_samples:long_name = "training data samples" ;
	  ubyte train_labels(train_num) ;
		  train_labels:long_name = "labels of training samples" ;
	  ubyte test_samples(test_num, height, width) ;
		  test_samples:long_name = "testing data samples" ;
	  ubyte test_labels(test_num) ;
		  test_labels:long_name = "labels of testing samples" ;

  // global attributes:
		  :url = "https://yann.lecun.com/exdb/mnist/" ;
  }
  ```

## Files in this directory
* [mnist.patch](./mnist.patch) --
  a patch file to be applied on
  [main.py](https://github.com/pytorch/examples/blob/main/mnist/main.py)
  once downloaded from [Pytorch Examples](https://github.com/pytorch/examples)
  before running the model training.

* [comm_file.py](./comm_file.py) --
  implements the parallel environment for training the model in parallel.

* [pnetcdf_io.py](./pnetcdf_io.py) --
  implements the file I/O using PnetCDF-Python.

* [create_mnist_netcdf.py](./create_mnist_netcdf.py) --
  a utility python program that reads the MINST files, extract a subset of the
  samples, and stores them into a newly created file in NetCDF format.

### Notes:
- The test set accuracy may vary slightly depending on how the data is distributed across the MPI processes.
- The accuracy and loss reported after each epoch are averaged across all MPI processes.

