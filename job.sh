#!/bin/bash

#SBATCH -A m844
#SBATCH -t 00:2:00 # Time limit => 2 min
#SBATCH -N 1
#SBATCH -C cpu
#SBATCH --qos=debug

#SBATCH -o qout.16.%j # std::out 输出到这个文件 
#SBATCH -e qout.16.%j 

#SBATCH --mail-type=end,fail
#SBATCH --mail-user=youjia@northwestern.edu

if test "x$SLURM_NTASKS_PER_NODE" = x ; then #number of cores per node
   SLURM_NTASKS_PER_NODE=16 # 256 maximum
fi

NUM_NODES=$SLURM_JOB_NUM_NODES

NP=$((NUM_NODES * SLURM_NTASKS_PER_NODE))

ulimit -c unlimited
module load conda
conda activate /global/common/software/m844/yll6162/conda_env/pnc


MPICH_MPIIO_DVS_MAXNODES=$NUM_NODES srun -n $NP -c 16 --cpu_bind=cores python ./test/tst_var_bput_varn.py # -c 2 => 128 process per node => 256/128=2
#srun python ...