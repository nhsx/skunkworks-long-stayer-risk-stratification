"""Utility methods for data manipulation"""
import csv
import logging
import os
from typing import Dict, Optional, List, Union, Iterable, Any

import numpy as np
import json

import stringcase

# Constants to initialise logging
LOG = logging.getLogger('ltss.utils')
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config')


def read_data_descriptors(key: str, file: str = os.path.join(CONFIG_DIR, 'data_description.json')) -> Optional[Union[List, Dict]]:
    """
    Retrieve data description list or dict from config file

    :param key: Key to object for retrieval in config file
    :param file: Path to JSON file containing data description fields
    :return: List/Dict of defined data fields
    """
    try:
        with open(file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        LOG.exception(e)
        return
    return data.get(key)


# Globals used for data description lookups to avoid multiple file read overheads
# Selectors - List of data fields to use as model inputs
MODEL_SELECTORS = read_data_descriptors('Model_Selectors')
# UI - Grouped lists of fields to serve for rendering in the UI
UI_FIELDS = read_data_descriptors('UI_Fields')
# Data scale factor for vector preparation
VECTOR_SCALE = 25


def flatten_vector(vector: Dict[str, Any]) -> np.array:
    """
    Flatten a vector dict using `MODEL_SELECTORS` to define the columns
    :param vector: Dict of vectorised field values keyed on field name
    :return: A flat numpy array of the fields used in the models
    """
    # Create a list of values using the chosen selectors, fill in -1 for missing values
    values = [vector.get(key, -1) for key in MODEL_SELECTORS]
    # Convert to numpy array
    return np.asarray(values)


def reshape_vector(vector: Dict) -> np.array:
    """
    Take vectorised data record and format to match expected model input shape

    :param vector: Dict of vectorised field values keyed on field name
    :return: An 8x8 numpy array of the fields expected by the prediction model
    """
    value_array = flatten_vector(vector)
    # Pad to 64 elements
    padded = np.zeros(64)
    padded[:value_array.shape[0]] = value_array
    # Reshape to 8x8
    reshaped = np.reshape(padded, (-1, 1, 8, 8))
    # Scale the data for convolution reasons
    scaled = reshaped * VECTOR_SCALE
    return scaled


def vector_to_dict(vector: np.array, scale_factor=1.0):
    """
    Given a vector produced by `reshape_vector`, reverse it back into a Dict
    :param vector: Padded vector to un-shape
    :param scale_factor: Divide vector values by this factor to undo any scaling (e.g., by reshape_vector)
    :return: A dict representing the values in the vector
    """
    vector /= scale_factor
    vector = vector.reshape(-1)
    return dict(zip(MODEL_SELECTORS, vector.tolist()))


def format_field_header(field: str) -> str:
    """Helper method to convert field header to consistent upper and snake case format"""
    # Ensure correct type and convert to lowercase
    header = str(field).lower()
    # Convert spaced words to snake case
    header = stringcase.snakecase(header)
    # Convert all characters to uppercase and return key
    return header.upper()


def format_field_value(value: Optional[str]) -> Optional[str]:
    """Helper method to format strings in lowercase and handle NoneType values gracefully"""
    if value is None:
        return
    return value.lower()


def format_record_for_frontend(record: Dict) -> Optional[List]:
    """
    Filters a patient record using list of desired UI fields from data config file

    :param record: Patient record dict keyed on field names
    :return: Patient record containing only whitelisted fields to send to the UI. Returned object is in the form of a
    list of dict objects to group similar fields in a known order.
    """
    if UI_FIELDS is None:
        return
    formatted_record = []
    # Format field name and value for each specified field and add to return record
    for category, fields in UI_FIELDS.items():
        formatted_record.append({format_field_header(field): format_field_value(record.get(field)) for field in fields})
    return formatted_record


def read_records_csv(path: str) -> Iterable[Dict[str, str]]:
    """
    Parse a record file into a generator of well-formatted record dictionaries, suitable for use in the vectoriser
    :param path: Path to the CSV file to to parse
    :return: Generator of record dicts
    """
    with open(path, 'r', encoding='utf-8-sig') as fp:
        reader = csv.DictReader(fp)
        # Read each row in the records file
        for row in reader:
            # Standardise row key and value formats and set 'null' default for missing values
            yield {format_field_header(k): v.lower() if v is not None else 'null' for k, v in row.items()}
