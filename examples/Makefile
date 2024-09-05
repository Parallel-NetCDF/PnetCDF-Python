#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

check_PROGRAMS = collective_write.py \
                 create_open.py \
                 fill_mode.py \
                 flexible_api.py \
                 get_info.py \
                 ghost_cell.py \
                 global_attribute.py \
                 hints.py \
                 put_varn_int.py \
                 transpose2D.py \
                 transpose.py \
                 put_vara.py \
                 get_vara.py


TESTS_ENVIRONMENT  = export check_PROGRAMS="${check_PROGRAMS}";
TESTS_ENVIRONMENT += export PNETCDF_DIR="${PNETCDF_DIR}";

OUTPUT_DIR = _tmp_output

all:

check: ptest4
	cd nonblocking && make check
	cd Pytorch_DDP && make check
	cd MNIST && make check

ptests: ptest3 ptest4 ptest8
	cd nonblocking && make ptests
	cd Pytorch_DDP && make ptests
	cd MNIST && make ptests

ptest3:
	@mkdir -p ${OUTPUT_DIR}
	@echo "======================================================================"
	@echo "    examples: Parallel testing on 3 MPI processes"
	@echo "======================================================================"
	@${TESTS_ENVIRONMENT} export NPROC=3; ./parallel_run.sh ${OUTPUT_DIR} || exit 1
	@echo ""

ptest4:
	@mkdir -p ${OUTPUT_DIR}
	@echo "======================================================================"
	@echo "    examples: Parallel testing on 4 MPI processes"
	@echo "======================================================================"
	@${TESTS_ENVIRONMENT} export NPROC=4; ./parallel_run.sh ${OUTPUT_DIR} || exit 1
	@echo ""

ptest8:
	@mkdir -p ${OUTPUT_DIR}
	@echo "======================================================================"
	@echo "    examples: Parallel testing on 8 MPI processes"
	@echo "======================================================================"
	@${TESTS_ENVIRONMENT} export NPROC=8; ./parallel_run.sh ${OUTPUT_DIR} || exit 1
	@echo ""

clean:
	rm -rf ${OUTPUT_DIR}
	cd nonblocking && make clean
	cd Pytorch_DDP && make clean
	cd MNIST && make clean

.PHONY: all check ptests ptest3 ptest4 ptest8 clean

