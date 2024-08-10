#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

check_PROGRAMS = mnist_main.py

MNIST_URL = https://raw.githubusercontent.com/pytorch/examples/main/mnist/main.py

mnist_main.py:
	curl -Ls $(MNIST_URL) -o $@
	patch -st $@ < mnist.patch

all:

ptests check: mnist_main.py mnist_images.nc
	@echo "======================================================================"
	@echo "    examples/MNIST: Parallel testing on 4 MPI processes"
	@echo "======================================================================"
	@mpiexec -n 4 python mnist_main.py --batch-size 4 --test-batch-size 2 --epochs 3 --input-file mnist_images.nc
	@echo ""

clean:
	rm -rf mnist_main.py

