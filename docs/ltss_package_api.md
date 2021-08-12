# Package API Documentation

Packages:

[ltss Package](#ltss-package)

Submodules:

- [ltss.vectorise](#ltssvectorise)
  - [Field Enum](#field-object)
  - [Mapping Object](#mapping-object)  
- [ltss.risk_model](#ltssvectorise)
  - [RiskCDFModel Object](#RiskCDFModel-object)
- [ltss.utils](#ltssutils)
- [ltss.los_model](#ltsslos_model)
    - [LoSPredictor Object](#lospredictor-object)
    

<a name="ltss"></a>
# LTSS Package

Flask app serving record and model prediction endpoints

<a name="ltss.initialise_models"></a>
### initialise\_models

```python
initialise_models()
```

Initialise both predictive models and persist to a global instance variable

<a name="ltss.create_app"></a>
### create\_app

```python
create_app()
```

Construct flask app and define API endpoints

<a name="ltss.vectorise"></a>
# ltss.vectorise

Patient record vectorisation module

<a name="ltss.vectorise.vectorise_record_list"></a>
### vectorise\_record\_list

```python
vectorise_record_list(records: Iterable[Dict]) -> Iterator[Dict]
```

Iterate over a list of raw patient records and returns a generator object for the vectorised records.

**Arguments**:

- `records`: Original record list

**Returns**:

Vectorised records list

<a name="ltss.vectorise.convert_value_type"></a>
### convert\_value\_type

```python
convert_value_type(value: Any) -> Optional[Union[str, int, float]]
```

Attempt to convert a record element to the most appropriate data type

**Arguments**:

- `value`: Value to interpret

**Returns**:

A correctly typed copy of the input value

<a name="ltss.vectorise.vectorise_record"></a>
### vectorise\_record

```python
vectorise_record(record: Dict[str, Any]) -> Dict[str, Any]
```

Vectorise a patient record.
Each field is processed to vector format based on a vector configuration specific to the field name and data type.

**Arguments**:

- `record`: Dictionary of record fields

**Returns**:

Vectorised record dict

<a name="ltss.vectorise.Field"></a>
### Field Object

```python
class Field(Enum)
```

Categorisation of field vectorisation methods

<a name="ltss.vectorise.Mapping"></a>
### Mapping Object

```python
class Mapping()
```

Class encapsulating data manipulations for vectorising each field in the patient record.
The vectorising blueprint is read from a file containing a type of manipulation for each field alongside a lookup
for certain types of field.

**Arguments**:

- `config_file`: Path to config file containing vectorisation blueprint

<a name="ltss.vectorise.Mapping.get_type"></a>
### get\_type

```python
 | get_type(key: str) -> Optional[Tuple]
```

Get vectorisation type for the named field

**Arguments**:

- `key`: Field name for lookup

**Returns**:

Vectorisation type

<a name="ltss.vectorise.Mapping.get_mapping"></a>
### get\_mapping

```python
 | get_mapping(key: str) -> Tuple[Optional[Iterable], Optional[Iterable]]
```

Get vectorisation mapping object(s) for the named field.
Return values are determined by the type of vectorisation required by the field.

**Arguments**:

- `key`: Field name for lookup

**Returns**:

Tuple of objects to indicate category numbers and/or code frequency buckets.

<a name="ltss.risk_model"></a>
# ltss.risk\_model

Risk stratification CDF model

<a name="ltss.risk_model.init_model"></a>
### init\_model

```python
init_model(model_file: str = 'config/risk_model.pickle') -> Optional[RiskCDFModel]
```

Initialise RiskCDFModel and load saved state from model file

**Arguments**:

- `model_file`: Path to model saved state pickle file

**Returns**:

RiskCDFModel instance

<a name="ltss.risk_model.get_prediction"></a>
### get\_prediction

```python
get_prediction(predictor: RiskCDFModel, vector: Dict, confidence: float = 0.95, ai_day_prediction: float = None) -> Dict
```

Interrogate the RiskCDFModel model for a set of predictions

**Arguments**:

- `predictor`: Initialised RiskCDFModel instance
- `vector`: Vectorised patient record
- `confidence`: Confidence level
- `ai_day_prediction`: Length of stay days prediction from AI model

**Returns**:

Dict of predicted results

<a name="ltss.risk_model.RiskCDFModel"></a>
## RiskCDFModel Object

```python
class RiskCDFModel()
```

Model designed to take, or infer, a length of stay and then using the cumulative density, predict with
a desired accuracy (p), what the likely maximum discharge day is.  This discharge day is then stratified to
give a risk of that patient staying past a long stay threshold.

The day predicted from the CDF can also be considered a personalised long stay estimate for that patient.  For
example, a child aged 9 should spend significantly less time in hospital before they become a worry of overstaying,
compared to patients with stroke.

<a name="ltss.risk_model.RiskCDFModel.load_state_dict"></a>
### load\_state\_dict

```python
 | load_state_dict(filename: str)
```

Load model distributions from file

**Arguments**:

- `filename`: Path to file containing model distributions

<a name="ltss.risk_model.RiskCDFModel.day_from_pdf"></a>
### day\_from\_pdf

```python
 | @staticmethod
 | day_from_pdf(pdf: np.array) -> int
```

Get day estimate from PDF using probabilities sum.
Sum uses trapz rule for non-integer intervals.

**Arguments**:

- `pdf`: Array of PDF probabilities from 0 - 30 days

**Returns**:

Day estimate

<a name="ltss.risk_model.RiskCDFModel.day_from_cdf"></a>
### day\_from\_cdf

```python
 | @staticmethod
 | day_from_cdf(cdf: np.array, confidence: float) -> int
```

Get day estimate from CDF using probabilities sum.
Sum uses trapz rule for non-integer intervals.

**Arguments**:

- `cdf`: Array of CDF probabilities from 0 - 30 days
- `confidence`: Confidence level

**Returns**:

Day estimate

<a name="ltss.risk_model.RiskCDFModel.risk_from_day"></a>
### risk\_from\_day

```python
 | @staticmethod
 | risk_from_day(day: float) -> int
```

Takes a day prediction and produced a stratified risk score

**Arguments**:

- `day`: Predicted stay in days

**Returns**:

Risk category in the range 1 - 5

<a name="ltss.risk_model.RiskCDFModel.risk_of_long_stay_by_category"></a>
### risk\_of\_long\_stay\_by\_category

```python
 | @staticmethod
 | risk_of_long_stay_by_category(category: int) -> int
```

Converts category to chance of long stay (from test data)
as a percentage.

For example: 0 (minor) => 1% chance of long stay
             1 (low risk) => 4% chance of long stay

**Arguments**:

- `category`: Risk band category

**Returns**:

Risk percentage based on training data

<a name="ltss.risk_model.RiskCDFModel.risk_by_cdf"></a>
### risk\_by\_cdf

```python
 | @staticmethod
 | risk_by_cdf(cdf: np.array) -> np.array
```

Converts CDF into risk band category

**Arguments**:

- `cdf`: CDF function

**Returns**:

Risk per band

<a name="ltss.risk_model.RiskCDFModel.risk_by_pdf"></a>
### risk\_by\_pdf

```python
 | @staticmethod
 | risk_by_pdf(pdf: np.array) -> np.array
```

Converts PDF into risk band category

**Arguments**:

- `pdf`: PDF function

**Returns**:

Risk per band

<a name="ltss.risk_model.RiskCDFModel.risk_and_day_from_record"></a>
### risk\_and\_day\_from\_record

```python
 | risk_and_day_from_record(record: Dict, confidence: float) -> Dict
```

Takes record as input and produced a risk score and day prediction based on a confidence by factor

**Arguments**:

- `record`: Patient record
- `confidence`: Confidence level

**Returns**:

Dict of day predictions and risk scores per factor

<a name="ltss.risk_model.RiskCDFModel.compute_from_record"></a>
### compute\_from\_record

```python
 | compute_from_record(record: Dict, confidence: float, use_max=True) -> Tuple[int, np.ndarray]
```

Return a risk profile based on the patient record

**Arguments**:

- `record`: Patient record
- `confidence`: Confidence level  
- `use_max`: Flag to indicate peak probability should be used

**Returns**:

day and probability based on population

<a name="ltss.risk_model.RiskCDFModel.risk_and_cat_by_record"></a>
### risk\_and\_cat\_by\_record

```python
 | risk_and_cat_by_record(record: Dict, confidence: float) -> Tuple[int, np.ndarray, Dict, str]
```

Produce risk category by record with confidence

**Arguments**:

- `record`: patient record
- `confidence`: pegged confidence of result being correct

**Returns**:

risk, risk_cat, risk_factors, highest_risk_factor (Biggest Risk as seen in the input data)

<a name="ltss.utils"></a>
# ltss.utils

Utility methods for data manipulation

<a name="ltss.utils.read_data_descriptors"></a>
### read\_data\_descriptors

```python
read_data_descriptors(key: str, file: str = 'config/data_description.json') -> Optional[Union[List, Dict]]
```

Retrieve data description list or dict from config file

**Arguments**:

- `key`: Key to object for retrieval in config file
- `file`: Path to JSON file containing data description fields

**Returns**:

List/Dict of defined data fields

<a name="ltss.utils.flatten_vector"></a>
### flatten\_vector

```python
flatten_vector(vector: Dict[str, Any]) -> np.array
```

Flatten a vector dict using `MODEL_SELECTORS` to define the columns

**Arguments**:

- `vector`: Dict of vectorised field values keyed on field name

**Returns**:

A flat numpy array of the fields used in the models

<a name="ltss.utils.reshape_vector"></a>
### reshape\_vector

```python
reshape_vector(vector: Dict) -> np.array
```

Take vectorised data record and format to match expected model input shape

**Arguments**:

- `vector`: Dict of vectorised field values keyed on field name

**Returns**:

An 8x8 numpy array of the fields expected by the prediction model

<a name="ltss.utils.vector_to_dict"></a>
### vector\_to\_dict

```python
vector_to_dict(vector: np.array, scale_factor=1.0)
```

Given a vector produced by `reshape_vector`, reverse it back into a Dict

**Arguments**:

- `vector`: Padded vector to un-shape
- `scale_factor`: Divide vector values by this factor to undo any scaling (e.g., by reshape_vector)

**Returns**:

A dict representing the values in the vector

<a name="ltss.utils.format_field_header"></a>
### format\_field\_header

```python
format_field_header(field: str) -> str
```

Helper method to convert field header to consistent upper and snake case format

<a name="ltss.utils.format_field_value"></a>
### format\_field\_value

```python
format_field_value(value: Optional[str]) -> Optional[str]
```

Helper method to format strings in lowercase and handle NoneType values gracefully

<a name="ltss.utils.format_record_for_frontend"></a>
### format\_record\_for\_frontend

```python
format_record_for_frontend(record: Dict) -> Optional[List]
```

Filters a patient record using list of desired UI fields from data config file

**Arguments**:

- `record`: Patient record dict keyed on field names

**Returns**:

Patient record containing only whitelisted fields to send to the UI. Returned object is in the form of a list of dict objects to group similar fields in a known order.

<a name="ltss.utils.read_records_csv"><a/>
### read\_records\_csv

```python
read_records_csv(path: str) -> Iterable[Dict[str, str]]
```

Parse a record file into a generator of well-formatted record dictionaries, suitable for use in the vectoriser

**Arguments**:
- `path`: Path to the CSV file to to parse

**Returns**:
Generator of record dicts

<a name="ltss.los_model"></a>
# ltss.los\_model

Length of stay AI model

<a name="ltss.los_model.init_model"></a>
### init\_model

```python
init_model(vector_dims: int = 1, feature_dims: int = 64, model_file: str = 'config/los_model.state') -> LoSPredictor
```

Initialise the LoSPredictor model and load saved state from model file

**Arguments**:

- `vector_dims`: Dimensionality of the patient record vectors
- `feature_dims`: Dimensionality (number of features) in the model input vector
- `model_file`: Path to model state file

**Returns**:

Constructed LoSPredictor instance

<a name="ltss.los_model.get_prediction"></a>
### get\_prediction

```python
get_prediction(predictor: LoSPredictor, vector: Dict[str, Any]) -> Dict
```

Interrogate the LoSPredictor model for a length of stay prediction

**Arguments**:

- `predictor`: Initialised LoSPredictor instance
- `vector`: Vectorised patient record

**Returns**:

Dict containing predicted length of stay result


<a name="ltss.los_model.LoSPredictor"></a>
## LoSPredictor Object

```python
class LoSPredictor(nn.Module)
```

This model will form the main discriminator for the GAN.  This will be used with the Realistic Outcome
Discriminator to supply feedback to the GAN, however it will provide a functional unit for generating
length of stay.

**Arguments**:

- `vector_d`: Dimensionality of the record vector
- `features_d`: Dimensionality of features

<a name="ltss.los_model.LoSPredictor.conv_block"></a>
#### conv\_block

```python
 | conv_block(in_channels: int, out_channels: int, kernel_size: Tuple[int, ...], stride: Tuple[int, ...], padding: Tuple[int, ...])
```

Convolutional block - ala DCGan

**Arguments**:

- `in_channels`: input vector shape
- `out_channels`: output vector shape
- `kernel_size`: kernel size for convolution
- `stride`: stride for convolution
- `padding`: padding for convolution

**Returns**:

N x out_channels vector


