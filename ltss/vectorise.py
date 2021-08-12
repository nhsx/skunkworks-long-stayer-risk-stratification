"""Patient record vectorisation module"""
import json
import logging
import os.path
from enum import Enum
from typing import Dict, Optional, Iterator, Tuple, Any, Union, Iterable, List

from ltss.utils import format_field_header

# Constants to initialise logging
LOG = logging.getLogger('ltss.vectorise')


class Field(Enum):
    """Categorisation of field vectorisation methods"""
    COPY = 1  # Copy value in existing form with no manipulation
    BINARY = 2  # Convert Y/N/NA/NULL to binary category (0/1)
    CATEGORISE = 3  # Convert text categories to integer based on given mapping
    CODE_LIST = 4  # A concatenated list of codes to convert to categories
    TOP_FREQUENCY_COUNT = 5  # Convert list to ordered binned frequency counts
    LENGTH_OF_STAY = 6  # Treat length of stay as special case - append to end of record
    AGE_CATEGORISE = 7  # Special case to categorise ages by dividing by 10


class Mapping:
    """
    Class encapsulating data manipulations for vectorising each field in the patient record.
    The vectorising blueprint is read from a file containing a type of manipulation for each field alongside a lookup
    for certain types of field.

    :param config_file: Path to config file containing vectorisation blueprint
    """
    _map: Dict

    @staticmethod
    def _mapping_decoder(value):
        """Custom decoder to correctly deserialise the Field Enum class from a JSON file"""
        if 'MAPPING_TYPE' in value:
            _, member = value['MAPPING_TYPE'].split('.')
            return getattr(Field, member)
        else:
            return value

    def __init__(self, config_file: str):
        try:
            with open(os.path.abspath(config_file), 'r') as fp:
                self._map = json.load(fp, object_hook=self._mapping_decoder)
        except:
            # Cannot vectorise without valid record mapping
            LOG.error(f'Cannot load vector mapping from given file \'{config_file}\'')
            raise ValueError

    def get_type(self, key: str) -> Optional[Tuple]:
        """Get vectorisation type for the named field

        :param key: Field name for lookup
        :return: Vectorisation type
        """
        mapped = self._map.get(key)
        return tuple(mapped, )[0] if mapped is not None else None

    def get_mapping(self, key: str) -> Tuple[Optional[Union[Dict, List]], Optional[Dict]]:
        """
        Get vectorisation mapping object(s) for the named field.
        Return values are determined by the type of vectorisation required by the field.

        :param key: Field name for lookup
        :return: Tuple of objects to indicate category numbers and/or code frequency buckets.
        """
        if key not in self._map:
            raise ValueError(f'No mapping exists for {key}')

        mapped = list(self._map.get(key))
        if len(mapped) > 2:
            # Freq count - List + Dict
            return mapped[1], mapped[2]
        elif len(mapped) > 1:
            # Category lookup or code list - Single Dict or List
            return mapped[1], None
        else:
            # No mapping objects available
            return None, None


# Global Mapping instance for field type and mappings lookup
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config')
FIELD_MANIPULATIONS = Mapping(os.path.join(CONFIG_DIR, 'model_vector_mappings.json'))


def vectorise_record_list(records: Iterable[Dict]) -> Iterator[Dict]:
    """
    Iterate over a list of raw patient records and returns a generator object for the vectorised records.
    :param records: Original record list
    :return: Vectorised records list
    """
    for record in records:
        yield vectorise_record(record)


def convert_value_type(value: Any) -> Optional[Union[str, int, float]]:
    """
    Attempt to convert a record element to the most appropriate data type
    :param value: Value to interpret
    :return: A correctly typed copy of the input value
    """
    # Check for possibly null/nan/missing values
    if value is None or str(value).lower() in ['null', 'nan', '']:
        return None
    if str(value).isnumeric():
        return int(value)
    try:
        return float(value)
    except ValueError:
        pass

    try:
        return str(value).lower()
    except:
        pass
    return value


def vectorise_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Vectorise a patient record.
    Each field is processed to vector format based on a vector configuration specific to the field name and data type.

    :param record: Dictionary of record fields
    :return: Vectorised record dict
    """
    vectorised_record = {}
    length_of_stay = None
    # Parse each field from the patient record and apply the manipulation from the FIELD_MANIPULATIONS mapping
    for field, value in record.items():
        # Standardise field key format
        field = format_field_header(field)
        # Handle missing values and attempt to correctly type data values
        value = convert_value_type(value)
        # Lookup the type of manipulation required for the field/value
        manipulation = FIELD_MANIPULATIONS.get_type(field)
        if manipulation is None:
            # No manipulation listed for the field, drop from vectorised record
            continue
        if manipulation is Field.COPY:
            # Copy field replacing null values and stripping leading/trailing whitespace
            if value is None:
                vectorised_record[field] = -1
            elif isinstance(value, str):
                stripped = str(value).strip()
                vectorised_record[field] = convert_value_type(stripped)
            else:
                vectorised_record[field] = value
        elif manipulation is Field.BINARY:
            # Convert binary flag to 0/1 value
            vectorised_record[field] = _binarise_value(value)
        elif manipulation is Field.AGE_CATEGORISE:
            # Copy age field as is
            vectorised_record[field] = value
            # Create additional age category field for age/10 value
            vectorised_record[f'{field}_CATEGORY'] = _categorise_age(value)
        elif manipulation is Field.CATEGORISE:
            # Convert category to scalar value based on mapping
            vectorised_record[field] = _categorise_value(value, field)
        elif manipulation is Field.LENGTH_OF_STAY:
            # Special case for length of stay - store value to append at the end
            length_of_stay = value
        elif manipulation is Field.CODE_LIST:
            # Generate expanded code list
            field_code_dict = _expand_code_field(value, field)
            vectorised_record.update(field_code_dict)
        elif manipulation is Field.TOP_FREQUENCY_COUNT:
            # Generate expanded code list
            field_code_dict = _expand_code_field(value, field)
            vectorised_record.update(field_code_dict)
            # Generate the binned top N code counts
            top_n_dict = _generate_top_n_counts(value, field)
            vectorised_record.update(top_n_dict)

    # Append original length of stay to the end of the vectorised record
    vectorised_record['LENGTH_OF_STAY'] = length_of_stay if length_of_stay is not None else -1
    return vectorised_record


def _binarise_value(value: Optional[str]) -> int:
    """Convert character encodings to a binary integer value"""
    if value is None or value.upper() != 'Y':
        return 0
    else:
        return 1


def _categorise_value(value: str, field: str) -> Optional[int]:
    """Convert a text string category to a scalar category number based on known mapping"""
    try:
        mapping, _ = FIELD_MANIPULATIONS.get_mapping(field)
    except:
        LOG.error(f'Error getting mapping for field: {field}')
        return

    if mapping is None or not isinstance(mapping, dict):
        LOG.error(f'Mapping object is not valid to perform category lookup for field: {field}, '
                  f'cannot vectorise value: {value}')
        return

    return mapping[value] if value in mapping else -1


def _categorise_age(value):
    """Convert full age number to an age category integer"""
    age = int(value)
    return int(age / 10)


def _expand_code_field(value: str, field: str) -> Optional[Dict]:
    """
    Expand field containing single string of codes to a dict keyed on field name + code concatenation.
    The expanded code dict will contain an element for all possible codes in the field and an associated binary flag
    to indicate if each of the codes is present in the record currently undergoing vectorisation.

    E.g.    > Field exists in the record named 'EXAMPLE' with full set of possible values being [A, B, C, D ,E ,F]
            > A patient record contains the code string "A, C, D"
            > The method will generate the following dictionary:
                {
                    EXAMPLE_CODE_A: 1,
                    EXAMPLE_CODE_B: 0,
                    EXAMPLE_CODE_C: 1,
                    EXAMPLE_CODE_D: 1,
                    EXAMPLE_CODE_E: 0,
                    EXAMPLE_CODE_F: 0
                }
    """
    try:
        # Retrieve the full list of potential codes found in the record field
        code_list, _ = FIELD_MANIPULATIONS.get_mapping(field)
    except:
        LOG.error(f'Error getting mapping for field: {field}')
        return
    if code_list is None or not isinstance(code_list, list):
        LOG.error(f'Mapping object is not valid to generate code list for field: {field}, cannot vectorise '
                  f'value: {value}')
        return

    if value is not None:
        if isinstance(value, str):
            # Split the string of codes from the patient record
            recorded_codes = value.split(',') if ',' in value else value.split()
        else:
            recorded_codes = [value] if not isinstance(value, list) else value
    else:
        recorded_codes = []

    # Create dict with key for all possible codes
    expanded_dict = {f'{field}_CODE_{code.upper()}': 0 for code in code_list}
    # Update binary identifier for codes present in the current record
    for code in list(recorded_codes):
        code = code.strip(';').strip() if isinstance(code, str) else code
        if code == 'null' or code == '':
            continue
        expanded_dict[f'{field}_CODE_{str(code).upper()}'] = 1
    return expanded_dict


def _generate_top_n_counts(value: str, field: str) -> Optional[Dict]:
    """
    Expand field containing single string of codes to a dict of the number of these codes that belong to the
    top X -> X+10 of all possible code values in the dataset.

    E.g     > Field exists in the record named 'EXAMPLE' with top 10 most frequently observed codes being [A,B,C,D,E,F,G,H,I,J],
            the top 11 - 20 being [K,L,M,N,O,P,Q,R,S,T] etc.
            > A patient record contains the code string "A, D, E, S, T"
            > The method will generate the following dictionary:
                {
                    EXAMPLE_N_TOP_0_TO_10: 3,
                    EXAMPLE_N_TOP_11_TO_20: 2,
                    EXAMPLE_N_TOP_21_TO_30: 0,
                    ...
                }
    """
    try:
        # Retrieve mappings for the codes in each top X -> X+10 range
        _, top_n_mapping = FIELD_MANIPULATIONS.get_mapping(field)
    except:
        LOG.error(f'Error getting mapping for field: {field}')
        return

    if top_n_mapping is None or not isinstance(top_n_mapping, dict):
        LOG.error(f'Mapping object not valid for to generate frequency counts for field {field}, cannot vectorise '
                  f'value: {value}')
        return

    if value is not None:
        if isinstance(value, str):
            # Split the string of codes from the patient record
            recorded_codes = value.split(',') if ',' in value else value.split()
        else:
            recorded_codes = [value] if not isinstance(value, list) else value
    else:
        recorded_codes = []

    # Create dict with key for each Top X -> X+10 range
    top_n_dict = {f'{field}_{key}': 0 for key in top_n_mapping.keys()}

    # Update Top X -> X+10 count for each code in the current record that is know to fall in this range
    for code in recorded_codes:
        code = code.strip(';').strip() if isinstance(code, str) else code
        if code == 'null' or code == '':
            continue
        for top_n_key, top_n_codes in top_n_mapping.items():
            if str(code) in top_n_codes:
                top_n_dict[f'{field}_{top_n_key}'] += 1

    return top_n_dict
