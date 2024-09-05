#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

check_PROGRAMS = mnist_main.py

MNIST_URL = https://raw.githubusercontent.com/pytorch/examples/main/mnist/main.py

all:

mnist_main.py:
	@curl -Ls $(MNIST_URL) -o $@
	@patch -st $@ < mnist.patch

MNIST_DATA_URL = https://yann.lecun.com/exdb/mnist

MNIST_DATASETS = train-images-idx3-ubyte \
                 train-labels-idx1-ubyte \
                 t10k-images-idx3-ubyte \
                 t10k-labels-idx1-ubyte

MNIST_DATASETS_GZ = $(MNIST_DATASETS:=.gz)

train-images-idx3-ubyte:
	@curl -LOsf $(MNIST_DATA_URL)/$@.gz
	@gunzip $@.gz

train-labels-idx1-ubyte:
	@curl -LOsf $(MNIST_DATA_URL)/$@.gz
	@gunzip $@.gz

t10k-images-idx3-ubyte:
	@curl -LOsf $(MNIST_DATA_URL)/$@.gz
	@gunzip $@.gz

t10k-labels-idx1-ubyte:
	@curl -LOsf $(MNIST_DATA_URL)/$@.gz
	@gunzip $@.gz

mnist_images.nc: $(MNIST_DATASETS)
	@python create_mnist_netcdf.py

ptests check: mnist_main.py
	@echo "======================================================================"
	@echo "    examples/MNIST: Parallel testing on 4 MPI processes"
	@echo "======================================================================"
	@mpiexec -n 4 python mnist_main.py --batch-size 4 --test-batch-size 2 --epochs 3 --input-file mnist_images.nc
	@echo ""

clean:
	rm -f mnist_main.py
	rm -f $(MNIST_DATASETS)
	rm -f $(MNIST_DATASETS_GZ)
	rm -rf __pycache__

.PHONY: all check ptests clean

