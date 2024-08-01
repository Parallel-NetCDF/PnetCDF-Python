import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR
import comm_file
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.distributed import ReduceOp, all_reduce
from pnetcdf import File
from mpi4py import MPI

class PnetCDFDataset(torch.utils.data.Dataset):
    def __init__(self, netcdf_file, data_var, label_var, transform=None, comm=MPI.COMM_WORLD):
        self.netcdf_file = netcdf_file
        self.data_var = data_var
        self.label_var = label_var
        self.transform = transform
        self.comm = comm

        # Open the NetCDF file
        self.f = File(self.netcdf_file, mode='r', comm=self.comm)
        self.f.begin_indep() # To use independent I/O mode

        # Get dimensions of the variables
        self.data_shape = self.f.variables[self.data_var].shape
        self.label_shape = self.f.variables[self.label_var].shape

    def __len__(self):
        return self.data_shape[0]

    def __getitem__(self, idx):
        # Read the data and label at the given index
        image = self.f.variables[self.data_var][idx, ...]
        label = self.f.variables[self.label_var][idx]

        if self.transform:
            image = self.transform(image)

        return image, label

    def close(self):
        self.f.close()

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


def train(args, model, device, train_loader, optimizer, epoch, comm):
    model.train()
    total_loss = 0.0
    num_batches = 0
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        num_batches += 1
        
    # Compute the average loss for the current epoch
    avg_loss = total_loss / num_batches
    
    # Reduce the average loss across all processes
    avg_loss_tensor = torch.tensor(avg_loss, device=device)
    all_reduce(avg_loss_tensor, op=ReduceOp.SUM)
    avg_loss_tensor /= comm.get_size()

    # Print the average loss only from the master process
    if comm.get_rank() == 0:
        print(f'Train Epoch: {epoch}\tAverage Loss: {avg_loss_tensor.item():.6f}')


def test(model, device, test_loader, comm):
    model.eval()
    test_loss = 0
    correct = 0
    total_samples = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()
            total_samples += data.size(0)

    test_loss_tensor = torch.tensor(test_loss, device=device)
    correct_tensor = torch.tensor(correct, device=device)
    total_samples_tensor = torch.tensor(total_samples, device=device)
    all_reduce(test_loss_tensor, op=ReduceOp.SUM)
    all_reduce(correct_tensor, op=ReduceOp.SUM)
    all_reduce(total_samples_tensor, op=ReduceOp.SUM)
    test_loss = test_loss_tensor.item()
    correct = correct_tensor.item()
    total_samples = total_samples_tensor.item()
    avg_loss = test_loss / total_samples
    accuracy = 100. * correct / total_samples
    
    if comm.get_rank() == 0:
        print(f'Test set: Average loss: {avg_loss:.4f}, Accuracy: {correct}/{total_samples} ({accuracy:.0f}%)\n')


def main():
    # Training settings
    parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
    parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                        help='input batch size for training (default: 64)')
    parser.add_argument('--test-batch-size', type=int, default=1000, metavar='N',
                        help='input batch size for testing (default: 1000)')
    parser.add_argument('--epochs', type=int, default=5, metavar='N',
                        help='number of epochs to train (default: 5)')
    parser.add_argument('--lr', type=float, default=1.0, metavar='LR',
                        help='learning rate (default: 1.0)')
    parser.add_argument('--gamma', type=float, default=0.7, metavar='M',
                        help='Learning rate step gamma (default: 0.7)')
    parser.add_argument('--no-cuda', action='store_true', default=False,
                        help='disables CUDA training')
    parser.add_argument('--no-mps', action='store_true', default=False,
                        help='disables macOS GPU training')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='quickly check a single pass')
    parser.add_argument('--seed', type=int, default=1, metavar='S',
                        help='random seed (default: 1)')
    parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                        help='how many batches to wait before logging training status')
    parser.add_argument('--save-model', action='store_true', default=False,
                        help='For Saving the current Model')
    parser.add_argument('--netcdf-file', type=str, default="../MNIST_data/mnist_images.nc",
                        help='netcdf file storing train and test data')
    args = parser.parse_args()
    use_cuda = not args.no_cuda and torch.cuda.is_available()
    use_mps = not args.no_mps and torch.backends.mps.is_available()

    ## init comm, rank, nprocs
    comm, device = comm_file.init_parallel()
    
    rank = comm.get_rank()
    nprocs = comm.get_size()
    mpi_comm = MPI.COMM_WORLD
    mpi_rank = mpi_comm.Get_rank()
    mpi_size = mpi_comm.Get_size()
    
    torch.manual_seed(args.seed)

    print("nprocs = ", nprocs, " rank = ",rank," device = ", device, " mpi_size = ", mpi_size, " mpi_rank = ", mpi_rank)

    train_kwargs = {'batch_size': args.batch_size//nprocs}
    test_kwargs = {'batch_size': args.test_batch_size}
    if use_cuda:
        cuda_kwargs = {'num_workers': 2,
                       'pin_memory': True,
                       'shuffle': False}
        train_kwargs.update(cuda_kwargs)
        test_kwargs.update(cuda_kwargs)

    transform=transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
        ])
    
    # pytorch MNIST datasets
    # dataset1 = datasets.MNIST('../MNIST_data', train=True, download=True,
    #                    transform=transform)
    # dataset2 = datasets.MNIST('../MNIST_data', train=False,
    #                    transform=transform)
    
    # pnetcdf MNIST datasets
    netcdf_file = args.netcdf_file
    dataset1 = PnetCDFDataset(netcdf_file, 'train_images', 'train_labels', transform, mpi_comm)
    dataset2 = PnetCDFDataset(netcdf_file, 'test_images', 'test_labels', transform, mpi_comm)
 
    # add train distributed sampler
    train_sampler = torch.utils.data.distributed.DistributedSampler(dataset1, num_replicas=comm.get_size(), rank=comm.get_rank(), shuffle=True)
    test_sampler = torch.utils.data.distributed.DistributedSampler(dataset2, num_replicas=comm.get_size(), rank=comm.get_rank(), shuffle=False)
    train_loader = torch.utils.data.DataLoader(dataset1, sampler=train_sampler, **train_kwargs)
    test_loader = torch.utils.data.DataLoader(dataset2, sampler=test_sampler, **test_kwargs, drop_last=False)

    model = Net().to(device)
    # add to use DDP
    model = DDP(model, device_ids=[device] if use_cuda else None)
    optimizer = optim.Adadelta(model.parameters(), lr=args.lr)

    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)
    for epoch in range(1, args.epochs + 1):
        # train sampler set epoch
        train_sampler.set_epoch(epoch)
        test_sampler.set_epoch(epoch)
        
        train(args, model, device, train_loader, optimizer, epoch, comm)
        test(model, device, test_loader, comm)
        scheduler.step()

    if args.save_model:
        if rank == 0:
            torch.save(model.state_dict(), "mnist_cnn.pt")
    
    # close the file
    dataset1.close()
    dataset2.close()
    comm.finalize()

if __name__ == '__main__':
    main()
