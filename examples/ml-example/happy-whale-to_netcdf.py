from PIL import Image
import os
import numpy as np
import pncpy
from mpi4py import MPI

# paths
TRAIN_IMAGES = '../../../exercise/whale-and-dolphin/train_images'
TEST_IMAGES = '../../../exercise/whale-and-dolphin/test_images'


def list_files(gtdir):
    file_list = []
    for root, dirs, files in os.walk(gtdir):
        for file in files:
            file_list.append(os.path.join(root,file))
    return file_list

def to_nc(file_list, comm, out_file_path='train_images.nc'):
    print ('=> Converting images to netcdf')
    rank = comm.Get_rank()
    size = comm.Get_size()
    count = 0
    if os.path.exists(out_file_path) and rank == 0:
        os.remove(out_file_path)
    with pncpy.File(out_file_path, mode = "w", format = "64BIT_DATA") as fnc:
        dim_y = fnc.def_dim("Y", 224)
        dim_x = fnc.def_dim("X", 224)
        dim_rgb = fnc.def_dim("RGB", 3)
        # define nc variable for each img
        for f_ in file_list:
            img_name = f_.split(os.sep)[-1]
            v = fnc.def_var(img_name, pncpy.NC_UBYTE, (dim_y, dim_x, dim_rgb))
            count = count + 1
        # put values into each nc variable
        fnc.enddef()
        sub_file_list = [img for i, img in enumerate(file_list) if i%size == rank]
        for f_ in sub_file_list:
            image = Image.open(f_)
            img_name = f_.split(os.sep)[-1]
            if image.mode == 'L':
                image = image.convert('RGB')
            image_data = image.resize((224,224))
            image_data = np.array(image_data)
            v = fnc.variables[img_name]
            v[:] = image_data
    print ('=> Total Images To Process : {}'.format(len(sub_file_list)))
    print('=>  Finished Converting images to netCDF')

def main():
    comm = MPI.COMM_WORLD
    # print('=> ========= Converting Train Images ========= <=')
    file_list = list_files(TRAIN_IMAGES)
    
    to_nc(file_list, comm, out_file_path='train_images.nc')
    print('=> ========= Converting Test Images ========= <=')
    # file_list = list_files(TEST_IMAGES)[:100]
    # tohdf5(file_list,out_file_path='test_images.hdf5')

if __name__ == "__main__":
    main()