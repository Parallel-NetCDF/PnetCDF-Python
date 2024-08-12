#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

# This is the I/O module for reading input samples using PnetCDF-Python

from mpi4py import MPI
from pnetcdf import File

class dataset():
    def __init__(self, path, samples, labels, transform=None, comm=None):
        self.path = path
        self.samples = samples
        self.labels = labels
        self.transform = transform
        self.comm = comm

        # Open the NetCDF file
        self.f = File(self.path, mode='r', comm=self.comm)
        self.f.begin_indep() # To use independent I/O mode

        # Get dimensions of the variables
        self.data_shape = self.f.variables[self.samples].shape
        self.label_shape = self.f.variables[self.labels].shape

    def __len__(self):
        return self.data_shape[0]

    def __getitem__(self, idx):
        # Read the data and label at the given index
        image = self.f.variables[self.samples][idx, ...]
        label = self.f.variables[self.labels][idx]

        if self.transform:
            image = self.transform(image)

        return image, label

    def close(self):
        self.f.close()

