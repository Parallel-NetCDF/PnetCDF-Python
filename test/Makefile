#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

check_PROGRAMS = tst_atts.py \
                 tst_copy_attr.py \
                 tst_default_format.py \
                 tst_dims.py \
                 tst_file_fill.py \
                 tst_file_inq.py \
                 tst_file_mode.py \
                 tst_rename.py \
                 tst_var_bput_var1.py \
                 tst_var_bput_vara.py \
                 tst_var_bput_varm.py \
                 tst_var_bput_varn.py \
                 tst_var_bput_var.py \
                 tst_var_bput_vars.py \
                 tst_var_def_fill.py \
                 tst_var_get_var1.py \
                 tst_var_get_vara.py \
                 tst_var_get_varm.py \
                 tst_var_get_varn.py \
                 tst_var_get_var.py \
                 tst_var_get_vars.py \
                 tst_var_iget_var1.py \
                 tst_var_iget_vara.py \
                 tst_var_iget_varm.py \
                 tst_var_iget_varn.py \
                 tst_var_iget_var.py \
                 tst_var_iget_vars.py \
                 tst_var_indexer.py \
                 tst_var_iput_var1.py \
                 tst_var_iput_vara.py \
                 tst_var_iput_varm.py \
                 tst_var_iput_varn.py \
                 tst_var_iput_var.py \
                 tst_var_iput_vars.py \
                 tst_var_put_var1.py \
                 tst_var_put_vara.py \
                 tst_var_put_varm.py \
                 tst_var_put_varn.py \
                 tst_var_put_var.py \
                 tst_var_put_vars.py \
                 tst_var_rec_fill.py \
                 tst_var_string.py \
                 tst_var_type.py \
                 tst_version.py \
                 tst_wait.py

TESTS_ENVIRONMENT = export check_PROGRAMS="${check_PROGRAMS}";
OUTPUT_DIR = _tmp_output

all:

check: ptest4
ptests: ptest3 ptest4 ptest8

ptest3:
	@mkdir -p ${OUTPUT_DIR}
	@echo "======================================================================"
	@echo "    test: Parallel testing on 3 MPI processes"
	@echo "======================================================================"
	@${TESTS_ENVIRONMENT} export NPROC=3; ./parallel_run.sh ${OUTPUT_DIR} || exit 1
	@echo ""

ptest4:
	@mkdir -p ${OUTPUT_DIR}
	@echo "======================================================================"
	@echo "    test: Parallel testing on 4 MPI processes"
	@echo "======================================================================"
	@${TESTS_ENVIRONMENT} export NPROC=4; ./parallel_run.sh ${OUTPUT_DIR} || exit 1
	@echo ""

ptest8:
	@mkdir -p ${OUTPUT_DIR}
	@echo "======================================================================"
	@echo "    test: Parallel testing on 8 MPI processes"
	@echo "======================================================================"
	@${TESTS_ENVIRONMENT} export NPROC=8; ./parallel_run.sh ${OUTPUT_DIR} || exit 1
	@echo ""

clean:
	rm -rf ${OUTPUT_DIR}
	rm -rf __pycache__

.PHONY: all check ptests ptest3 ptest4 ptest8 clean

