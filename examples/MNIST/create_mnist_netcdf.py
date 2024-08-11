#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

import os, argparse, struct
import numpy as np
from array import array

from mpi4py import MPI
import pnetcdf

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


def to_nc(train_samples, train_labels, test_samples, test_labels, out_file_path='mnist_images.nc'):
    if os.path.exists(out_file_path):
        os.remove(out_file_path)

    train_labels = list(train_labels)
    test_labels = list(test_labels)

    with pnetcdf.File(out_file_path, mode = "w", format = "NC_64BIT_DATA") as fnc:

        # Each image is of dimension 28 x 28
        dim_y = fnc.def_dim("height", 28)
        dim_x = fnc.def_dim("width", 28)

        # define number of traing and testing samples
        dim_train = fnc.def_dim("train_num", len(train_samples))
        dim_test = fnc.def_dim("test_num", len(test_samples))

        # define nc variables to store training image samples and labels
        train_data = fnc.def_var("train_samples", pnetcdf.NC_UBYTE, (dim_train, dim_y, dim_x))
        train_data.long_name = "training data samples"
        train_label = fnc.def_var("train_labels", pnetcdf.NC_UBYTE, (dim_train))
        train_label.long_name = "labels of training samples"

        # define nc variables to store testing image samples and labels
        test_data = fnc.def_var("test_samples", pnetcdf.NC_UBYTE, (dim_test, dim_y, dim_x))
        test_data.long_name = "testing data samples"
        test_label = fnc.def_var("test_labels", pnetcdf.NC_UBYTE, (dim_test))
        test_label.long_name = "labels of testing samples"

        # exit define mode and enter data mode
        fnc.enddef()

        # write training data samples
        for idx, img in enumerate(train_samples):
            train_data[idx, :, :] = img

        # write labels of training data samples
        train_label[:] = np.array(train_labels, dtype = np.uint8)

        # write testing data samples
        for idx, img in enumerate(test_samples):
            test_data[idx, :, :] = img

        # write labels of testing data samples
        test_label[:] = np.array(test_labels, dtype = np.uint8)


if __name__ == '__main__':

    # parse command-line arguments
    args = None
    parser = argparse.ArgumentParser(description='Store MNIST Datasets to a NetCDF file')
    parser.add_argument("--verbose", help="Verbose mode", action="store_true")
    parser.add_argument('--train-size', type=int, default=60, metavar='N',
                        help='Number of training samples extracted from the input file (default: 60)')
    parser.add_argument('--test-size', type=int, default=12, metavar='N',
                        help='Number of testing samples extracted from the input file (default: 12)')
    parser.add_argument("--train-data-file", nargs=1, type=str, help="(Optional) input file name of training data",\
                         default = "train-images-idx3-ubyte")
    parser.add_argument("--train-label-file", nargs=1, type=str, help="(Optional) input file name of training labels",\
                         default = "train-labels-idx1-ubyte")
    parser.add_argument("--test-data-file", nargs=1, type=str, help="(Optional) input file name of testing data",\
                         default = "t10k-images-idx3-ubyte")
    parser.add_argument("--test-label-file", nargs=1, type=str, help="(Optional) input file name of testing labels",\
                         default = "t10k-labels-idx1-ubyte")
    args = parser.parse_args()

    verbose = True if args.verbose else False

    if verbose:
        print("Input file of training samples: ", args.train_data_file)
        print("Input file of training labels:  ", args.train_label_file)
        print("Input file of testing  samples: ", args.test_data_file)
        print("Input file of testing  labels:  ", args.test_label_file)

    #
    # Load MINST dataset
    #
    mnist_dataloader = MnistDataloader(args.train_data_file,
                                       args.train_label_file,
                                       args.test_data_file,
                                       args.test_label_file)

    (train_data, train_label), (test_data, test_label) = mnist_dataloader.load_data()

    n_train = len(train_data)
    if args.train_size > 0 and args.train_size < n_train:
        n_train = int(args.train_size)

    n_test = len(test_data)
    if args.test_size > 0 and args.test_size < n_test:
        n_test = int(args.test_size)

    if verbose:
        print("Number of training samples:     ", n_train)
        print("Number of testing  samples:     ", n_test)

    #
    # create mini MNIST file in NetCDF format
    #
    to_nc(train_data[0:n_train], train_label[0:n_train],
           test_data[0:n_test],   test_label[0:n_test], "mnist_images.nc")


