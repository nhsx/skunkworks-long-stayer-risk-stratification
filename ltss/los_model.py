"""Length of stay AI model"""
from typing import Dict, Tuple, Any

import torch
import torch.nn as nn

from .utils import reshape_vector


class LoSPredictor(nn.Module):
    """
    This model will form the main discriminator CNN to predict Length of Stay (LoS).

    :param vector_d: Dimensionality of the record vector
    :param features_d: Dimensionality of features
    """
    def __init__(self, vector_d, features_d):
        # Init parent class
        super(LoSPredictor, self).__init__()

        # Our kernel, stride and padding parameters for each of our convolutional layers
        self.kernel_size = 4
        self.stride = 1
        self.padding = 1

        # The number of values we want to predict, we just want 1 output, LoS
        self.output_values = 1

        self.pred = nn.Sequential(
            # DC Gan does not use Batch normalisation for its first layer
            # Here we will input a batch by features, by IxJ. We have 53 elements in our feature vector, which we will
            # pad to 64 elements in our data-loader and reshape to 8x8 matrix for the convolutions.

            # Input Shape          : N x F x 8 x 8
            nn.Conv2d(vector_d, features_d, kernel_size=self.kernel_size,
                      stride=self.stride, padding=self.padding),
            # Output of Layer 1    : N x F x 7 x 7
            nn.LeakyReLU(0.2),
            # Output of ReLU       : N x F x 7 x 7
            self.conv_block(features_d, features_d * 2, self.kernel_size, self.stride, self.padding),
            # Output of DC Layer 2 : N x 2F x 6 x 6
            self.conv_block(features_d * 2, features_d * 4, self.kernel_size, self.stride, self.padding),
            # Output of DC Layer 3 : N x 4F x 5 x 5
            self.conv_block(features_d * 4, features_d * 8, self.kernel_size, self.stride, self.padding),
            # Output of DC Layer 4 : N x 8F x 4 x 4

            # Final layer, from DC-GAN, converges down output values (here 1 value per record, LoS)
            nn.Conv2d(features_d * 8, self.output_values, kernel_size=self.kernel_size, stride=self.stride, padding=0),
            # Output of Final Layer: N x 1 x 1 x 1

            # predictions from 0 - n only please, negative days are not acceptable
            nn.ReLU()
        )

    def conv_block(self, in_channels: int, out_channels: int, kernel_size: Tuple[int, ...], stride: Tuple[int, ...],
                   padding: Tuple[int, ...]):
        """
        Convolutional block - ala DCGan

        :param in_channels: input vector shape
        :param out_channels: output vector shape
        :param kernel_size: kernel size for convolution
        :param stride: stride for convolution
        :param padding: padding for convolution
        :return: N x out_channels vector
        """
        return nn.Sequential(
            # Convolutional layer
            nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size,
                      # Here the bias is set to false as we are going to use a batch norm
                      stride=stride, padding=padding, bias=False),
            # Normalisation
            nn.BatchNorm2d(out_channels),
            # Allows a small positive gradient when value is < 0.
            # if x > 0 then x else w, where w is some gradient.
            nn.LeakyReLU(0.2),
        )

    def forward(self, x):
        return self.pred(x)


def init_model(vector_dims: int = 1, feature_dims: int = 64,
               model_file: str = 'config/los_model.state') -> LoSPredictor:
    """
    Initialise the LoSPredictor model and load saved state from model file

    :param vector_dims: Dimensionality of the patient record vectors
    :param feature_dims: Dimensionality (number of features) in the model input vector
    :param model_file: Path to model state file
    :return: Constructed LoSPredictor instance
    """
    # Setup the model and load the checkpoint
    predictor = LoSPredictor(vector_dims, features_d=feature_dims)
    predictor.load_state_dict(torch.load(model_file, map_location=torch.device('cpu')))
    predictor.eval()
    return predictor


def get_prediction(predictor: LoSPredictor, vector: Dict[str, Any]) -> Dict:
    """
    Interrogate the LoSPredictor model for a length of stay prediction

    :param predictor: Initialised LoSPredictor instance
    :param vector: Vectorised patient record
    :return: Dict containing predicted length of stay result
    """
    # Convert numpy array into Torch tensor
    tensor = torch.Tensor(reshape_vector(vector))
    # Return tensor containing predicted value
    prediction = predictor(tensor)
    # Extract numerical prediction from tensor and return it
    reshaped = float(prediction.reshape(-1).item())
    return {'PREDICTED_LOS': reshaped}
