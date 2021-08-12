import argparse
import os.path
from typing import Optional, List
from tqdm import tqdm
from datetime import datetime
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from loader import DataHandler
# Adjust sys.path to allow access to ltss module in parent directory
import sys
sys.path.append('..')
from ltss.los_model import LoSPredictor


def run_training(loader: DataHandler, use_device: torch.device, checkpoint: Optional[str] = None,
                 number_epochs: int = 500, batches_per_epoch: int = 100, batch_size: int = 512, vector_d: int = 1,
                 features_d: int = 64, learning_rate: int = 2e-4, validation_size: int = 10000,
                 save_frequency: Optional[int] = 100):
    """
    Run the main training loop, on the specific device, using the specified training/test data
    :param loader: The DataHandler to use to load train and test data splits
    :param use_device: The torch device to use (specifying GPU/CPU)
    :param checkpoint: If specific, resume training from the given checkpoint file
    :param number_epochs: The number of training epochs to run
    :param batches_per_epoch: The number of batch iterations to use per training epoch
    :param batch_size: The number of training samples to use per batch
    :param vector_d: The feature vector dimensionality (vector_d x features_d)
    :param features_d: The number of features to expect in the feature vector (vector_d x features_d)
    :param learning_rate: The learning rate used in the optimiser
    :param validation_size: The number of validation samples to use
    :param save_frequency: Save a model checkpoint every N epochs
    """
    # Get the time at the start of the run, and start a logging session using Tensorboard
    now = datetime.now()
    run_dir = os.path.abspath(f'runs/exp_{now.strftime("%d_%m_%Y_%H_%M_%S")}')
    print(f'Saving tensorboard output to {run_dir}')
    writer = SummaryWriter(run_dir)
    # Create the predictor for our single channel vector, using the number of features in the paper.
    disc = LoSPredictor(vector_d, features_d=features_d).to(device=use_device)
    # Load the state dict, otherwise torch will randomise
    if checkpoint is not None:
        disc.load_state_dict(torch.load(checkpoint))
    # Setup the base params of the optimiser
    opt_disc = optim.Adam(disc.parameters(), lr=learning_rate, betas=(0.5, 0.999))
    # We will use MSE as the loss function for the LoS
    criterion = nn.MSELoss().to(device=use_device)
    # Place our model into training mode
    disc.train()
    # Get a subset of validation data and move to GPU once
    validation_data, validation_los = loader.get_validation(validation_size)
    # Start training
    with tqdm(range(number_epochs)) as progress:
        for epoch in progress:
            # Set our loss to 0, which we will accumulate on every epoch.
            running_loss = 0
            # Main training batch loop
            for _ in np.arange(0, batches_per_epoch):
                # Get sample data
                sample, los_pdf = loader.get_training_n(batch_size)
                # remove the gradients from the optimiser
                opt_disc.zero_grad()
                # Get the prediction
                pdf = disc(sample).reshape(-1)
                # Compute the loss between are real LoS and and our prediction
                loss = criterion(pdf, los_pdf)
                # tick up our loss (accumulated)
                running_loss += loss
                # zeroes the gradient buffers of all parameters
                disc.zero_grad()
                # back prop of gradients
                loss.backward()
                # Actually updates the model
                opt_disc.step()
                # The optimiser will now have concluded, and we can push through the next batch

            # Periodically save model output
            if save_frequency is not None and epoch % save_frequency == 0:
                torch.save(disc.state_dict(), f'mod_ep_{epoch}')

            # Compute MSE on training data from running_loss
            mse = running_loss / batches_per_epoch

            # Compute validation accuracy
            pdf = disc(validation_data).reshape(-1)
            errors = (validation_los - pdf).cpu().detach().numpy()
            mean_error = float(np.mean(errors))
            loa = float(np.std(errors) * 1.96)

            # Write accuracy data to tensorboard
            writer.add_scalar('Training MSE', mse, epoch)
            writer.add_scalar('Validation MSE', np.mean(np.power(errors, 2)), epoch)
            writer.add_scalar('Validation Mean Error', mean_error, epoch)
            writer.add_scalar('Validation Limits of Agreement', loa, epoch)

            # Update tqdm progress bar with accuracy data
            progress.set_postfix_str(f'MSE: {mse:.2f} days / {mse:.2f} days. LoA: {mean_error:.2f} ± {loa:.2f}')
        # Save the final discriminator state
        torch.save(disc.state_dict(), f'mod_ep_{epoch + 1}')


def parse_args(override_args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments. By default, parses sys.argv - if supplied, uses `args` as an override
    :param override_args: Optional override for command-line arguments
    :return: An argparse.Namespace containing the parsed argument set
    """
    parser = argparse.ArgumentParser(description='Train DC-GAN Discriminator model')
    parser.add_argument('--data', '-d', type=str, help='Input CSV data file', required=True)
    parser.add_argument('--checkpoint', '-c', type=str, help='Optional checkpoint file to resume from')
    parser.add_argument('--cpu', action='store_true', help='Disable CUDA, running all training on the CPU')
    parser.add_argument('--epochs', '-e', type=int, help='Number of epochs to run for', default=500)
    parser.add_argument('--batches-per-epoch', '-b', type=int, help='Number of batches per epoch', default=100)
    parser.add_argument('--batch-size', '-s', type=int, help='Batch size (number of samples per batch)', default=512)
    parser.add_argument('--validation-size', '-v', type=int, help='Number of validation samples to use', default=10000)
    parser.add_argument('--shuffle-data', action='store_true', help='Whether to shuffle data before sampling')
    parser.add_argument('--shuffle-seed', type=int, help='Optionally seed the PRNG for consistent shuffling')
    parser.add_argument('--max-samples', type=int, help='Maximum number of records to use for train/test splits')
    parser.add_argument('--save-frequency', type=int, help='Save a model checkpoint every N epochs')
    return parser.parse_args(args=override_args)


if __name__ == '__main__':
    # Parse command-line arguments
    args = parse_args()
    # Device setup, here we can turn off CUDA manually, or use it if it is available on our hardware
    use_cuda = not args.cpu
    device = torch.device('cuda' if use_cuda and torch.cuda.is_available() else 'cpu')
    # Load our data handler, which will feed our model with records from our 'training' cut.
    data_loader = DataHandler(args.data, device=device, shuffle=args.shuffle_data, fixed_seed=args.shuffle_seed,
                              max_samples=args.max_samples, reshape=True)
    print(f'Loaded {data_loader}')
    # Run the training loop
    run_training(data_loader, device, checkpoint=args.checkpoint, number_epochs=args.epochs,
                 batches_per_epoch=args.batches_per_epoch, batch_size=args.batch_size,
                 validation_size=args.validation_size, save_frequency=args.save_frequency)
