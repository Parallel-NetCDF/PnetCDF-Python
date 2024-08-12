#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

check_PROGRAMS = torch_ddp_skeleton.py


TESTS_ENVIRONMENT  = export check_PROGRAMS="${check_PROGRAMS}";
TESTS_ENVIRONMENT += export PNETCDF_DIR="${PNETCDF_DIR}";

OUTPUT_DIR = _tmp_output

all:

check: ptest4
ptests: ptest3 ptest4 ptest8

ptest3:
	@mkdir -p ${OUTPUT_DIR}
	@echo "======================================================================"
	@echo "    examples/Pytorch_DDP: Parallel testing on 3 MPI processes"
	@echo "======================================================================"
	@${TESTS_ENVIRONMENT} export NPROC=3; ./parallel_run.sh ${OUTPUT_DIR} || exit 1
	@echo ""

ptest4:
	@mkdir -p ${OUTPUT_DIR}
	@echo "======================================================================"
	@echo "    examples/Pytorch_DDP: Parallel testing on 4 MPI processes"
	@echo "======================================================================"
	@${TESTS_ENVIRONMENT} export NPROC=4; ./parallel_run.sh ${OUTPUT_DIR} || exit 1
	@echo ""

ptest8:
	@mkdir -p ${OUTPUT_DIR}
	@echo "======================================================================"
	@echo "    examples/Pytorch_DDP: Parallel testing on 8 MPI processes"
	@echo "======================================================================"
	@${TESTS_ENVIRONMENT} export NPROC=8; ./parallel_run.sh ${OUTPUT_DIR} || exit 1
	@echo ""

clean:
	rm -rf ${OUTPUT_DIR}

.PHONY: all check ptests ptest3 ptest4 ptest8 clean

