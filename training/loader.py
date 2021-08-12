from typing import Iterable, Tuple, Optional

import torch
import numpy as np
from tqdm import tqdm

import sys

sys.path.append('..')
from ltss.utils import read_records_csv, reshape_vector, flatten_vector
from ltss.vectorise import vectorise_record


class DataHandler(object):
    """
    Contains logic for loading data from the provided NHS CSV, filtering out non-major cases, and vectorising the
    resulting records for training (depending heavily on the parsing and vectorising logic in the `ltss` module).

    Additionally contains logic for consistently sampling the training and test splits.
    """

    def __init__(self, filename: str, max_samples=None, filter_minor=True, max_los_clip=30,
                 shuffle=False, fixed_seed=None, train_proportion=0.8, reshape=False, use_tqdm=True,
                 device: torch.device = torch.device('cpu')):
        self.device = device
        self.train_proportion = train_proportion
        self.max_samples = max_samples
        self.shuffle = shuffle
        self.fixed_seed = fixed_seed
        self.filter_minor = filter_minor
        self.max_los_clip = max_los_clip
        self.reshape = reshape
        # Build a random instance for this handler - if methods are called in the same order, this behaviour will give
        # consistent sampling throughout the lifetime of the handler
        if self.fixed_seed is not None:
            np.random.seed(self.fixed_seed)
        # Stream the records from CSV, vectorise, and store in a stack
        data, los = zip(*self.__stream_records(filename, use_tqdm, filter_minor, max_los_clip, max_samples, reshape))
        # Stack data and los for storage
        self.data = np.vstack(data)
        self.los = np.vstack(los)
        # Drop the extra dimension from the LoS array
        self.los = self.los.reshape(-1)
        # Carve data into train/test sets
        training_indices, test_indices = self.__train_test_splits()
        self.train_data = self.data[training_indices]
        self.train_los = self.los[training_indices]
        self.test_data = self.data[test_indices]
        self.test_los = self.los[test_indices]

    @staticmethod
    def __stream_records(filename: str, use_tqdm: bool, filter_minor: bool, max_los_clip: Optional[int],
                         max_samples: Optional[int], reshape: bool) -> Iterable[Tuple[np.array, int]]:
        """
        Stream records off disk, vectorise them, and optionally filter out "minor" records from the data
        :param filename: The filename of raw CSV data to parse
        :param use_tqdm: If true, display TQDM progress info (useful when there is a lot of data to load and vectorise)
        :param filter_minor: If true, discard entries for the IS_MAJOR is not true
        :param max_los_clip: If non-none, clip the maximum LoS to this value
        :param max_samples: If non-none, limit the number of records emitted
        :param reshape: Whether to flatten and reshape the vector, or only flatten it (impacts output data shape)
        :return: Generator of tuples of 8x8 feature vectors, and their ground-truth length of stay
        """
        stream = read_records_csv(filename)
        if use_tqdm:
            stream = tqdm(stream, desc='Loading data', unit=' records')
        emitted_samples = 0
        for record in stream:
            vector = vectorise_record(record)
            los = vector['LENGTH_OF_STAY']
            # Discard obviously bad data (negative LoS is impossible)
            if los < 0:
                continue
            # Filter out "minor" records
            if filter_minor and vector['IS_MAJOR'] != 1:
                continue
            # Clip LoS to a maximum value
            if max_los_clip is not None:
                los = min(los, max_los_clip)
            if reshape:
                yield reshape_vector(vector), los
            else:
                yield flatten_vector(vector), los
            # Update stats
            emitted_samples += 1
            if use_tqdm:
                stream.set_postfix_str(f'generated {emitted_samples} good records', refresh=False)
            # If we've emitted enough samples, finish fast
            if max_samples is not None and emitted_samples >= max_samples:
                return

    def __train_test_splits(self):
        """
        Make reproducible train/test splits of the data. Optionally, shuffle (reproducibly, controlled by
        `self.shuffle` and `self.fixed_seed`) the data for train/test.
        :return:
        """
        # By default, our indices are just 0-n
        split_indices = list(range(len(self.data)))
        # If shuffling, use our shared Random instance to shuffle our indices before slicing
        if self.shuffle:
            np.random.shuffle(split_indices)
        # Regardless of shuffle, take the first self.train_proportion for training, and the last
        # 1 - self.train_proportion records as test
        train_n = int(self.train_proportion * len(self.data))
        training_indices = split_indices[:train_n]
        test_indices = split_indices[train_n:]
        return training_indices, test_indices

    def __sample(self, data, los, n: Optional[int], random: bool):
        """
        Sample the given data/los distribution, selecting the given N and optionally randomising the sample.
        :param data: Dataset of vectors to sample
        :param los: Dataset of lengths of stay to sample
        :param n: The number of samples to generate
        :param random: When true, randomise samples
        :return: Torch tensors for the sampled data and los distributions, moved to the relevant Torch device.
        """
        if n is None:
            n = len(data)
        else:
            n = min(len(data), n)
        # Uniform random sampling from our data array
        indices = list(range(len(data)))
        if random:
            np.random.shuffle(indices)
        indices = indices[:n]
        data = torch.Tensor(data[indices])
        los = torch.Tensor(los[indices])
        if self.device != 'cpu' and 'cuda' in self.device.type:
            data = data.cuda()
            los = los.cuda()
        return data, los

    def get_training_n(self, n: Optional[int] = None, random: bool = True) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Sample n records from the training data, optionally at random
        :param n: Number of samples to retrieve. Must be <= len(self.train_data)
        :param random: When true, randomise the retrieved samples
        :return: Tuple of training data and associated lengths of stay
        """
        return self.__sample(self.train_data, self.train_los, n, random)

    def get_validation(self, n: Optional[int] = None, random: bool = False) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Sample n records from the test data, optionally at random
        :param n: Number of samples to retrieve. Must be <= len(self.test_data)
        :param random: When true, randomise the retrieved samples
        :return: Tuple of test data and associated lengths of stay
        """
        return self.__sample(self.test_data, self.test_los, n, random)

    def __str__(self):
        config = dict(
            device=self.device,
            train_proportion=self.train_proportion,
            max_samples=self.max_samples,
            shuffle=self.shuffle,
            fixed_seed=self.fixed_seed,
            filter_minor=self.filter_minor,
            max_los_clip=self.max_los_clip,
            reshape=self.reshape,
        )
        return f'DataHandler: {len(self.data)} records, with {len(self.train_data)} training and ' \
               f'{len(self.test_data)} test records with configuration: ' \
               f'{{{", ".join([f"{k}={v}" for k, v in sorted(config.items())])}}}'
