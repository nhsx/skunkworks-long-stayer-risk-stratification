import argparse
import os.path
from typing import Optional, List

import numpy as np
import pandas as pd
import pickle
from loader import DataHandler
# Adjust sys.path to allow access to ltss module in parent directory
import sys
sys.path.append('..')
from ltss.risk_model import RiskCDFModel


class TrainableCDFModel(RiskCDFModel):
    """
        This model is designed to take, or infer, a length of stay and then using the cumulative density, predict with
        a desired accuracy (p), what the likely maximum discharge day is.  This discharge day is then stratified to
        give a risk of that patient staying past a long stay threshold.

        The day predicted from the CDF can also be considered a personalised long stay estimate for that patient.  For
        example, a child aged 9 should spend significantly less time in hospital before they become a worry of
        overstaying, compared to patients with stroke.
    """

    def __init__(self, loader: DataHandler):
        """
        Initialised the model, loading the data needed to create the relevant distributions
        :param loader: The DataHandler to use to load train and test data splits
        """
        super().__init__()
        data, los = loader.get_training_n()
        # Ensure tensors are in-memory and convert to numpy arrays
        data = data.cpu().detach().numpy()
        los = los.cpu().detach().numpy()
        # Convert numpy matrices to a pandas DataFrame
        self.data = self.data_to_pandas(data, los)

    def data_to_pandas(self, data: np.ndarray, los: np.ndarray) -> pd.DataFrame:
        """
        Given numpy arrays sampled by the `DataHandler`, construct a Pandas DataFrame for fast slicing
        when building the distributions.

        Assumes that `self.selectors` is in the same order as the feature vector.
        :param data: The feature vectors created by the `DataHandler`
        :param los: The associated lengths of stay for the given vectors
        :return: A Pandas DataFrame with columns given by `self.selectors`, and values from `data` and `los`
        """
        # Reshape data for indexing by selector
        data = data.reshape((data.shape[0], -1))
        assert data.shape[1] >= len(self.selectors), f'More selectors ({len(self.selectors)}) ' \
                                                     f'than vector entries ({data.shape[1]})'
        # Drop any non-selector padding
        data = data[:, :len(self.selectors)]
        # Expand dims on LoS array so it can be stacked
        los = np.expand_dims(los, 1)
        return pd.DataFrame(data=np.hstack((data, los)), columns=self.selectors + ['LENGTH_OF_STAY'])

    def generate_dists(self, normalise=False, cumulative=True):
        """
        Builds the distributions for calculating the stay probability. By default this produces non-normalised PDFs.
        To produce cdfs, cumulative must be True.
        :param normalise: Normalise the probabilities by the mean of the distributions
        :param cumulative: Produce CDFs rather than PDFs
        """
        # Create a dictionary for our distributions
        distribution_dict = {}

        # Base distribution is set between 0 - 30 days.  We consider greater than 30 day stays to be uniform
        # probability, and essentially an anomalous stay.  This was supported by our initial factor analysis.
        self.base_distribution = np.arange(0, 30)
        # Crib out the LoS
        length_of_stay_score = self.data['LENGTH_OF_STAY']

        # For each day, calculate the number of patients that stayed that number of days
        for day in np.arange(0, 30):
            self.base_distribution[day] = np.sum(length_of_stay_score == day)

        # Then produce a PDF by normalising.
        self.base_distribution = self.base_distribution / np.sum(self.base_distribution)

        # Now we iterate over our selectors, which will use each column as a filter
        for selector in self.selectors:
            # Dont process LoS, this is used only for fitting
            if selector == 'LENGTH_OF_STAY':
                continue
            # We will store each selector in its own dictionary
            selector_dict = {}
            # This collects each level in the selector, so it could be binary (is_cancer) or coding (1,2,3 .. ) Age
            # category
            cats = np.unique(self.data[selector])
            # Iterate over the codings
            for cat in cats:
                # Get the lengths of stay for that level in that selector
                length_of_stay_score = self.data.loc[self.data[selector] == cat]['LENGTH_OF_STAY']

                # Create a histogram
                stay_counts = np.zeros(30)
                for day in np.arange(0, 30):
                    # Set that count to the count of the matching records
                    stay_counts[day] = np.sum(length_of_stay_score == day)

                # Probability is the sum over the sum of all counts - if no days stayed, stay probability is just 0
                total_days_stayed = np.sum(stay_counts)
                stay_probability = stay_counts / total_days_stayed if total_days_stayed > 0 else stay_counts

                # Do we want the difference from some base prob
                # Disabled by default
                if normalise:
                    stay_probability -= self.base_distribution

                # Do we want the cumulative prob, for confidence (the default)
                if cumulative:
                    stay_probability = np.cumsum(stay_probability)

                # Store that away in our dictionary
                selector_dict[cat] = stay_probability

            # Finally, store the our levels dictionary in our main dictionary
            distribution_dict[selector] = selector_dict

        # store our distribution dict
        self.distributions = distribution_dict

        # Store away our setting
        self.cumulative = cumulative

    def save_state_dict(self, filename):
        """
        Saves the distribution states to a pickle file.
        :param filename: Where to save the pickle file
        """
        # State dictionary
        state = dict(
            distributions=self.distributions,
            base_distribution=self.base_distribution,
            cumulative=self.cumulative
        )
        # Write the file
        with open(filename, 'wb') as f:
            pickle.dump(state, f)


def run_training(loader: DataHandler, save_path: str) -> TrainableCDFModel:
    """
    Make a RiskCDFModel that is trained using the data in the given loader, saving its trained state to the given file
    :param loader: The DataHandler responsible for loading and vectorising the data
    :param save_path: The path to save the resulting trained model state to
    :return: A fully trained RiskCDFModel
    """
    # Load our distributions builder
    dist_builder = TrainableCDFModel(loader)
    # We want the true probability for each category and the cumulative dist function (the defaults)
    dist_builder.generate_dists()
    # Save trained state
    save_path = os.path.abspath(save_path)
    print(f'Saving distribution data to {save_path}')
    dist_builder.save_state_dict(save_path)
    return dist_builder


def plot_distributions(dist_builder: RiskCDFModel):
    """
    Given a trained RiskCDFModel, plot the CDFs for each category as a validation step
    :param dist_builder: The trained RiskCDFModel to plot distributions from
    """
    from matplotlib import pyplot as plt
    # Grab the distributions
    dist = dist_builder.distributions
    # Get all the selectors
    selectors = dist_builder.selectors
    for selector in selectors:
        plt.figure()
        plt.title(selector)
        plt.xlabel('Days')
        plt.ylabel('Cumulative confidence of Discharge')
        legend = []
        for key in dist[selector]:
            plt.plot(dist[selector][key])
            legend.append(key)
        plt.legend(legend)
        plt.show()


def parse_args(override_args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments. By default, parses sys.argv - if supplied, uses `args` as an override
    :param override_args: Optional override for command-line arguments
    :return: An argparse.Namespace containing the parsed argument set
    """
    parser = argparse.ArgumentParser(description='Train CDFM Risk Scoring Model')
    parser.add_argument('--data', '-d', type=str, help='Input CSV data file', required=True)
    parser.add_argument('--save-path', '-s', type=str, help='Path to save trained model data to', required=True)
    parser.add_argument('--shuffle-data', action='store_true', help='Whether to shuffle data before sampling')
    parser.add_argument('--shuffle-seed', type=int, help='Optionally seed the PRNG for consistent shuffling')
    parser.add_argument('--max-samples', type=int, help='Maximum number of records to use for train/test splits')
    parser.add_argument('--plot-distributions', action='store_true', help='Plot distribution summaries')
    return parser.parse_args(args=override_args)


if __name__ == '__main__':
    # Parse command-line arguments
    args = parse_args()
    # Load our data handler, which will feed our model with records from our 'training' cut.
    data_loader = DataHandler(args.data, shuffle=args.shuffle_data, fixed_seed=args.shuffle_seed,
                              max_samples=args.max_samples, reshape=False)
    print(f'Loaded {data_loader}')
    # Run the training loop
    builder = run_training(data_loader, save_path=args.save_path)
    # Optionally, plot distributions
    if args.plot_distributions:
        plot_distributions(builder)
