"""Risk stratification CDF model"""
import logging
from typing import Optional, Dict, Tuple

import numpy as np
import pickle

from ltss.utils import read_data_descriptors

# Constants to initialise logging
LOG = logging.getLogger('ltss.utils')


class RiskCDFModel:
    """
    Model designed to take, or infer, a length of stay and then using the cumulative density, predict with
    a desired accuracy (p), what the likely maximum discharge day is.  This discharge day is then stratified to
    give a risk of that patient staying past a long stay threshold.

    The day predicted from the CDF can also be considered a personalised long stay estimate for that patient.  For
    example, a child aged 9 should spend significantly less time in hospital before they become a worry of overstaying,
    compared to patients with stroke.
    """

    def __init__(self):
        # Read the selectors list from file and raise exception if none can be found
        self.selectors = read_data_descriptors('Model_Selectors')
        if self.selectors is None:
            raise ValueError('Error retrieving model selectors from file')
        # Data members to use during analysis
        self.distributions = None
        self.base_distribution = None
        self.cumulative = None

    def load_state_dict(self, filename: str):
        """Load model distributions from file

        :param filename: Path to file containing model distributions
        """
        try:
            with open(filename, 'rb') as handle:
                state = pickle.load(handle)
        except Exception as e:
            LOG.exception(e)
            raise e
        self.distributions = state.get("distributions")
        self.base_distribution = state.get("base_distribution")
        self.cumulative = state.get("cumulative")
        # Check all distributions have been read successfully
        if any(a is None for a in [self.distributions, self.base_distribution, self.cumulative]):
            LOG.error('Distribution required by CDF model is None')
            raise ValueError

    @staticmethod
    def day_from_pdf(pdf: np.array) -> int:
        """
        Get day estimate from PDF using probabilities sum.
        Sum uses trapz rule for non-integer intervals.

        :param pdf: Array of PDF probabilities from 0 - 30 days
        :return: Day estimate
        """
        return np.sum(np.arange(0, 30) * pdf).item()

    @staticmethod
    def day_from_cdf(cdf: np.array, confidence: float) -> int:
        """
        Get day estimate from CDF using probabilities sum.
        Sum uses trapz rule for non-integer intervals.

        :param cdf: Array of CDF probabilities from 0 - 30 days
        :param confidence: Confidence level
        :return: Day estimate
        """
        # Find where the the days are > than the confidence level
        day = np.where(cdf > confidence)
        # If we are not confident, set to the last day before long stay
        if np.size(day) == 0:
            return 20
        return day[0][0].item()  # first day > conf

    @staticmethod
    def risk_from_day(day: float) -> int:
        """
        Takes a day prediction and produced a stratified risk score
        :param day: Predicted stay in days
        :return: Risk category in the range 1 - 5
        """

        # Categories based on a 95% confidence interval, based on the training data
        day_thresholds = [6, 11, 13, 15]

        if day <= day_thresholds[0]:
            return 1
        if day < day_thresholds[1]:
            return 2
        if day <= day_thresholds[2]:
            return 3
        if day <= day_thresholds[3]:
            return 4
        return 5

    @staticmethod
    def risk_of_long_stay_by_category(category: int) -> int:
        """
        Converts category to chance of long stay (from test data)
        as a percentage.

        For example: 0 (minor) => 1% chance of long stay
                     1 (low risk) => 4% chance of long stay

        :param category: Risk band category
        :return: Risk percentage based on training data
        """

        # Categories based on a 95% confidence interval, based on the training data
        risk_bands = [1, 2, 17, 48, 68, 70]
        if 0 <= category <= 5:
            return risk_bands[category]

    @staticmethod
    def risk_by_cdf(cdf: np.array) -> np.array:
        """
        Converts CDF into risk band category
        :param cdf: CDF function
        :return: Risk per band
        """
        risk_cdf = RiskCDFModel.risk_by_pdf(np.diff(cdf))
        return risk_cdf

    @staticmethod
    def risk_by_pdf(pdf: np.array) -> np.array:
        """
        Converts PDF into risk band category
        :param pdf: PDF function
        :return: Risk per band
        """
        risk_pdf = [
            np.sum(pdf[0:5]),
            np.sum(pdf[6:9]),
            np.sum(pdf[10:13]),
            np.sum(pdf[14:15]),
            np.sum(pdf[16:])
        ]
        return np.array(risk_pdf)

    def risk_and_day_from_record(self, record: Dict, confidence: float) -> Dict:
        """
        Takes record as input and produced a risk score and day prediction based on a confidence by factor
        :param record: Patient record
        :param confidence: Confidence level
        :return: Dict of day predictions and risk scores per factor
        """
        factors_labels = {}
        for selector in self.selectors:
            key = record[selector]
            cdf = self.distributions.get(selector, dict()).get(key)
            if cdf is not None:
                day = self.day_from_cdf(cdf, confidence)
                risk = self.risk_from_day(day)
                risk_pdf = self.risk_by_cdf(cdf)
                factors_labels[selector] = dict(
                    day=day,
                    risk=risk,
                    risk_pdf=risk_pdf)
        return factors_labels

    def compute_from_record(self, record: Dict, confidence: float, use_max=True) -> Tuple[int, np.ndarray]:
        """
        Return a risk profile based on the patient record
        :param record: Patient record
        :param confidence: Confidence level
        :param use_max: Flag to indicate peak probability should be used
        :return: day and probability based on population
        """
        # The model excludes non-major patients so a standard fallback prediction is issued for these patients.
        if record.get("IS_MAJOR", 1) == 0:
            # Use fallback pdf for minor patients
            pdf = np.zeros(30)
            pdf[0] = 0.97
            pdf[1] = 0.02
            pdf[2] = 0.01
            return 0, pdf

        # Create a blank PDF
        pdf = np.zeros(30)
        count = 0

        # For each of our selectors get the probability
        for selector in self.selectors:
            key = record.get(selector)
            if key in self.distributions.get(selector):
                pdf += self.distributions.get(selector).get(key)
                count += 1

        # If there were any probabilities associated with our keys, create the normalised PDF
        if count > 0:
            pdf = pdf / count
        else:
            # Just use the base PDF as that is our best guess when no other data is available
            pdf = self.base_distribution

        # If we are not using the max
        if not use_max:
            # Are we using the CDF
            if self.cumulative:
                # Return day based on CDF
                return self.day_from_cdf(pdf, confidence=confidence), pdf
            # Otherwise return day based on PDF
            return self.day_from_pdf(pdf), pdf
        else:
            # Otherwise we just return the maximum likelihood based on the pdf (note this is for further processing,
            # actual probability should be the area to that point.
            return np.where(pdf == np.max(pdf)).item(), pdf

    def risk_and_cat_by_record(self, record: Dict, confidence: float) -> Tuple[int, np.ndarray, Dict, str]:
        """
        Produce risk category by record with confidence
        :param record: patient record
        :param confidence: Confidence level
        :return: risk, risk_cat, risk_factors, highest_risk_factor (Biggest Risk as seen in the input data)
        """

        # Start by getting the risk by day for each key
        risk_per_factor = self.risk_and_day_from_record(record, confidence=confidence)

        # Init variables for calculating the risks and factors
        scores = []
        risk_pdf = np.zeros(5)
        highest_risk_factor = None
        highest_risk_value = 0
        risk_factors = {}

        # For each key in our risk
        for key in risk_per_factor.keys():
            # If the risk is greater than our current highest risk factor, store it
            if risk_pdf[4] > highest_risk_value:
                highest_risk_value = risk_pdf[4]
                highest_risk_factor = key
            # Then collect that score
            scores.append(risk_per_factor[key]['risk'])
            # Add that to our PDF
            risk_pdf += risk_per_factor[key]['risk_pdf']
            # Store that as a key
            risk_factors[key] = risk_per_factor[key]['risk']

        # Normalise our risk PDF
        risk_pdf = risk_pdf / len(risk_per_factor)
        # Take the minimum of our maxed score criterion to get a most likely worst case
        risk_category = np.min(scores)
        # Return the risk cat, probability based on all factors and the most risky factor
        return risk_category, risk_pdf, risk_factors, highest_risk_factor


def init_model(model_file: str = 'config/risk_model.pickle') -> Optional[RiskCDFModel]:
    """
    Initialise the DistributionBuilder model and load saved state from model file

    :param model_file: Path to model saved state pickle file
    :return: DistributionBuilder instance
    """
    distribution_model = RiskCDFModel()
    distribution_model.load_state_dict(model_file)
    return distribution_model


def get_prediction(predictor: RiskCDFModel, vector: Dict, confidence: float = 0.95,
                   ai_day_prediction: float = None) -> Dict:
    """
    Interrogate the DistributionBuilder model for a set of predictions

    :param predictor: Initialised DistributionBuilder instance
    :param vector: Vectorised patient record
    :param confidence: Confidence level
    :param ai_day_prediction: Length of stay days prediction from AI model
    :return: Dict of predicted results
    """
    day, pdf = predictor.compute_from_record(vector, confidence=confidence, use_max=False)
    risk, risk_category, risk_factor, biggest_risk = predictor.risk_and_cat_by_record(vector, confidence=confidence)
    percentage_risk = predictor.risk_of_long_stay_by_category(risk)

    risk_ceiling = risk
    if ai_day_prediction is not None:
        # Using LoS day prediction from AI model, calculate a risk level
        ai_risk = predictor.risk_from_day(ai_day_prediction)
        # Carry forward the higher of the two risk scores
        risk_ceiling = ai_risk if ai_risk > risk else risk

    prediction = dict(
        RISK_STRATIFICATION=int(risk_ceiling),
        RISK_CAT_PROB_GENERAL_1=risk_category[0],
        RISK_CAT_PROB_GENERAL_2=risk_category[1],
        RISK_CAT_PROB_GENERAL_3=risk_category[2],
        RISK_CAT_PROB_GENERAL_4=risk_category[3],
        RISK_CAT_PROB_GENERAL_5=risk_category[4],
        BIGGEST_RISK_FACTOR=biggest_risk,
        RISK_BY_CATEGORY=risk_factor,
        PERCENTAGE_RISK_CAT=percentage_risk,
        MOT_DAYS=int(day),
    )

    return prediction
