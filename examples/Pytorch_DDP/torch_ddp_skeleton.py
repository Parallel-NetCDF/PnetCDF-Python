#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.

# This is a skeleton program to show how to run Pytorch distributed environment
# with MPI

import os
import torch
import torch.distributed as dist
from mpi4py import MPI

class distributed():
    def get_size(self):
        if dist.is_available() and dist.is_initialized():
            size = dist.get_world_size()
        else:
            size = 1
        return size

    def get_rank(self):
        if dist.is_available() and dist.is_initialized():
            rank = dist.get_rank()
        else:
            rank = 0
        return rank

    def get_local_rank(self):
        if not (dist.is_available() and dist.is_initialized()):
            return 0
        # Number of GPUs per node
        if torch.cuda.is_available():
            local_rank = dist.get_rank() % torch.cuda.device_count()
        else:
            # raise NotImplementedError()
            # running on cpu device should not call this function
            local_rank = -1
        return local_rank

    def __init__(self, method):
        # MASTER_PORT - required; has to be a free port on machine with rank 0
        # MASTER_ADDR - required (except for rank 0); address of rank 0 node
        # WORLD_SIZE - required; can be set either here, or in a call to init function
        # RANK - required; can be set either here, or in a call to init function
    
        if method == "nccl-slurm":
            # MASTER_ADDR can be set in the slurm batch script using command
            # scontrol show hostnames $SLURM_JOB_NODELIST
            if "MASTER_ADDR" not in os.environ:
                # Try SLURM_LAUNCH_NODE_IPADDR but it is the IP address of the node
                # from which the task launch was initiated (where the srun command
                # ran from). It may not be the node of rank 0.
                if "SLURM_LAUNCH_NODE_IPADDR" in os.environ:
                    os.environ["MASTER_ADDR"] = os.environ["SLURM_LAUNCH_NODE_IPADDR"]
                else:
                    raise Exception("Error: nccl-slurm - SLURM_LAUNCH_NODE_IPADDR is not set")
    
            # Use the default pytorch port
            if "MASTER_PORT" not in os.environ:
                if "SLURM_SRUN_COMM_PORT" in os.environ:
                    os.environ["MASTER_PORT"] = os.environ["SLURM_SRUN_COMM_PORT"]
                else:
                    os.environ["MASTER_PORT"] = "29500"
    
            # obtain WORLD_SIZE
            if "WORLD_SIZE" not in os.environ:
                if "SLURM_NTASKS" in os.environ:
                    world_size = os.environ["SLURM_NTASKS"]
                else:
                    if "SLURM_JOB_NUM_NODES" in os.environ:
                        num_nodes = os.environ["SLURM_JOB_NUM_NODES"]
                    else:
                        raise Exception("Error: nccl-slurm - SLURM_JOB_NUM_NODES is not set")
                    if "SLURM_NTASKS_PER_NODE" in os.environ:
                        ntasks_per_node = os.environ["SLURM_NTASKS_PER_NODE"]
                    elif "SLURM_TASKS_PER_NODE" in os.environ:
                        ntasks_per_node = os.environ["SLURM_TASKS_PER_NODE"]
                    else:
                        raise Exception("Error: nccl-slurm - SLURM_(N)TASKS_PER_NODE is not set")
                    world_size = ntasks_per_node * num_nodes
                os.environ["WORLD_SIZE"] = str(world_size)
    
            # obtain RANK
            if "RANK" not in os.environ:
                if "SLURM_PROCID" in os.environ:
                    os.environ["RANK"] = os.environ["SLURM_PROCID"]
                else:
                    raise Exception("Error: nccl-slurm - SLURM_PROCID is not set")
    
            # Initialize DDP module
            dist.init_process_group(backend = "nccl", init_method='env://')
    
        elif method == "nccl-openmpi":
            if "MASTER_ADDR" not in os.environ:
                if "PMIX_SERVER_URI2" in os.environ:
                    os.environ["MASTER_ADDR"] = os.environ("PMIX_SERVER_URI2").split("//")[1]
                else:
                    raise Exception("Error: nccl-openmpi - PMIX_SERVER_URI2 is not set")
    
            # Use the default pytorch port
            if "MASTER_PORT" not in os.environ:
                os.environ["MASTER_PORT"] = "29500"
    
            if "WORLD_SIZE" not in os.environ:
                if "OMPI_COMM_WORLD_SIZE" not in os.environ:
                    raise Exception("Error: nccl-openmpi - OMPI_COMM_WORLD_SIZE is not set")
                os.environ["WORLD_SIZE"] = os.environ["OMPI_COMM_WORLD_SIZE"]
    
            if "RANK" not in os.environ:
                if "OMPI_COMM_WORLD_RANK" not in os.environ:
                    raise Exception("Error: nccl-openmpi - OMPI_COMM_WORLD_RANK is not set")
                os.environ["RANK"] = os.environ["OMPI_COMM_WORLD_RANK"]
    
            # Initialize DDP module
            dist.init_process_group(backend = "nccl", init_method='env://')
    
        elif method == "nccl-mpich":
            if "MASTER_ADDR" not in os.environ:
                os.environ['MASTER_ADDR'] = "localhost"
    
            # Use the default pytorch port
            if "MASTER_PORT" not in os.environ:
                os.environ["MASTER_PORT"] = "29500"
    
            if "WORLD_SIZE" not in os.environ:
                if "PMI_SIZE" in os.environ:
                    world_size = os.environ["PMI_SIZE"]
                elif MPI.Is_initialized():
                    world_size = MPI.COMM_WORLD.Get_size()
                else:
                    world_size = 1
                os.environ["WORLD_SIZE"] = str(world_size)
    
            if "RANK" not in os.environ:
                if "PMI_RANK" in os.environ:
                    rank = os.environ["PMI_RANK"]
                elif MPI.Is_initialized():
                    rank = MPI.COMM_WORLD.Get_rank()
                else:
                    rank = 0
                os.environ["RANK"] = str(rank)

            # Initialize DDP module
            dist.init_process_group(backend = "nccl", init_method='env://')
    
        elif method == "gloo":
            if "MASTER_ADDR" not in os.environ:
                # check if OpenMPI is used
                if "PMIX_SERVER_URI2" in os.environ:
                    addr = os.environ["PMIX_SERVER_URI2"]
                    addr = addr.split("//")[1].split(":")[0]
                    os.environ["MASTER_ADDR"] = addr
                else:
                    os.environ['MASTER_ADDR'] = "localhost"
    
            # Use the default pytorch port
            if "MASTER_PORT" not in os.environ:
                os.environ["MASTER_PORT"] = "29500"
    
            # obtain WORLD_SIZE
            if "WORLD_SIZE" not in os.environ:
                # check if OpenMPI is used
                if "OMPI_COMM_WORLD_SIZE" in os.environ:
                    world_size = os.environ["OMPI_COMM_WORLD_SIZE"]
                elif "PMI_SIZE" in os.environ:
                    world_size = os.environ["PMI_SIZE"]
                elif MPI.Is_initialized():
                    world_size = MPI.COMM_WORLD.Get_size()
                else:
                    world_size = 1
                os.environ["WORLD_SIZE"] = str(world_size)
    
            # obtain RANK
            if "RANK" not in os.environ:
                # check if OpenMPI is used
                if "OMPI_COMM_WORLD_RANK" in os.environ:
                    rank = os.environ["OMPI_COMM_WORLD_RANK"]
                elif "PMI_RANK" in os.environ:
                    rank = os.environ["PMI_RANK"]
                elif MPI.Is_initialized():
                    rank = MPI.COMM_WORLD.Get_rank()
                else:
                    rank = 0
                os.environ["RANK"] = str(rank)
    
            # Initialize DDP module
            dist.init_process_group(backend = "gloo", init_method='env://')
    
        else:
            raise NotImplementedError()
    
    def finalize(self):
        dist.destroy_process_group()

#----< init_parallel() >-------------------------------------------------------
def init_parallel():
    # check if cuda device is available
    ngpu_per_node = torch.cuda.device_count()
    if not torch.cuda.is_available():
        backend = "gloo"
    else:
        backend = "nccl-mpich"

    # initialize parallel/distributed environment
    comm = distributed(backend)
    rank = comm.get_rank()
    world_size = comm.get_size()
    local_rank = comm.get_local_rank()

    # select training device: cpu or cuda
    if not torch.cuda.is_available():
        device = torch.device("cpu")
    else:
        device = torch.device("cuda:"+str(local_rank))

    return comm, device

#----< main() >----------------------------------------------------------------
def main():
    # initialize parallel environment
    comm, device = init_parallel()

    rank = comm.get_rank()
    nprocs = comm.get_size()

    print("nprocs = ", nprocs, " rank = ",rank," device = ", device)

    comm.finalize()

if __name__ == "__main__":
    main()

