import os
import numpy as np
import numpy as np
import pnetcdf
from mpi4py import MPI
from array import array
import struct

class MnistDataloader(object):
    def __init__(self, training_images_filepath,training_labels_filepath,
                 test_images_filepath, test_labels_filepath):
        self.training_images_filepath = training_images_filepath
        self.training_labels_filepath = training_labels_filepath
        self.test_images_filepath = test_images_filepath
        self.test_labels_filepath = test_labels_filepath
    
    def read_images_labels(self, images_filepath, labels_filepath):        
        labels = []
        with open(labels_filepath, 'rb') as file:
            magic, size = struct.unpack(">II", file.read(8))
            if magic != 2049:
                raise ValueError('Magic number mismatch, expected 2049, got {}'.format(magic))
            labels = array("B", file.read())        
        
        with open(images_filepath, 'rb') as file:
            magic, size, rows, cols = struct.unpack(">IIII", file.read(16))
            if magic != 2051:
                raise ValueError('Magic number mismatch, expected 2051, got {}'.format(magic))
            image_data = array("B", file.read())   
        images = []
        for i in range(size):
            images.append([0] * rows * cols)
        for i in range(size):
            img = np.array(image_data[i * rows * cols:(i + 1) * rows * cols])
            img = img.reshape(28, 28)
            images[i][:] = img            
        
        return images, labels
            
    def load_data(self):
        x_train, y_train = self.read_images_labels(self.training_images_filepath, self.training_labels_filepath)
        x_test, y_test = self.read_images_labels(self.test_images_filepath, self.test_labels_filepath)
        return (x_train, y_train),(x_test, y_test)  

#
# Set file paths based on added MNIST Datasets
#
input_path = '.'
training_images_filepath = os.path.join(input_path, 'train-images-idx3-ubyte/train-images-idx3-ubyte')
training_labels_filepath = os.path.join(input_path, 'train-labels-idx1-ubyte/train-labels-idx1-ubyte')
test_images_filepath = os.path.join(input_path, 't10k-images-idx3-ubyte/t10k-images-idx3-ubyte')
test_labels_filepath = os.path.join(input_path, 't10k-labels-idx1-ubyte/t10k-labels-idx1-ubyte')

#
# Load MINST dataset
#
mnist_dataloader = MnistDataloader(training_images_filepath, training_labels_filepath, test_images_filepath, test_labels_filepath)
(x_train, y_train), (x_test, y_test) = mnist_dataloader.load_data()

# use partial dataset
x_train_small = x_train[:60]
y_train_small = y_train[:60]
x_test_small = x_test[:12]
y_test_small = y_test[:12]

def to_nc(train_samples, test_samples, train_labels, test_labels, comm, out_file_path='mnist_images.nc'):
    if os.path.exists(out_file_path):
        os.remove(out_file_path)
    train_labels = list(train_labels)
    test_labels = list(test_labels)
    with pnetcdf.File(out_file_path, comm= comm, mode = "w", format = "64BIT_DATA") as fnc:
        
        dim_y = fnc.def_dim("Y", 28)
        dim_x = fnc.def_dim("X", 28)
        dim_num_train = fnc.def_dim("train_idx", len(train_samples))
        dim_num_test = fnc.def_dim("test_idx", len(test_samples))

        # define nc variable for all imgs
        v_train = fnc.def_var("train_images", pnetcdf.NC_UBYTE, (dim_num_train, dim_x, dim_y))
        # put labels into attributes
        v_label_train = fnc.def_var("train_labels", pnetcdf.NC_UBYTE, (dim_num_train, ))
        
                # define nc variable for all imgs
        v_test = fnc.def_var("test_images", pnetcdf.NC_UBYTE, (dim_num_test, dim_x, dim_y))
        # put labels into attributes
        v_label_test = fnc.def_var("test_labels", pnetcdf.NC_UBYTE, (dim_num_test, ))
        
        # put values into each nc variable
        fnc.enddef()
        v_label_train[:] = np.array(train_labels, dtype = np.uint8)
        for idx, img in enumerate(train_samples):
            v_train[idx, :, :] = img
            
        v_label_test[:] = np.array(test_labels, dtype = np.uint8)
        for idx, img in enumerate(test_samples):
            v_test[idx, :, :] = img

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# create mini MNIST file
to_nc(x_train_small, x_test_small, y_train_small, y_test_small, comm, "mnist_images_mini.nc")

# create MNIST file
# to_nc(x_train, x_test, y_train, y_test, comm, "mnist_images.nc")


