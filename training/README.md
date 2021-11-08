# Length of Stay & LTSS Risk Scoring Model Training
## Summary of Models
This directory contains training code for two models: a DC-GAN discriminator CNN to predict Length of Stay (LoS), and 
a cumulative density based Long-Term Stay Score (LTSS) risk stratification model.

The LoS model takes in a short-form set of fields, which are those available to staff in the ED upon patient 
presentation. The CNN attempts to predict a likely stay (in days) based on that initial information.  

The CDF model uses this prediction in conjunction with the distributions of all stays, and a pegged confidence (95%), 
to predict the number of days required to medically optimise the patient, and to score the overall risk of them
becoming a "long stayer". This risk score is the ultimate model output that is useful to clinicians.

## Experimental Results

The overall model produces very good risk stratification, with Risk Category 1 consisting of 99% short stayers, and 
minor cases, with less than 1% of long-stayers being classified as very low risk. Moreover, 66% of all long-stayers 
are classified as Risk Category 4 and 5, with proportions steadily increasing through these categories.

The CNN yields very noisy results, with a median error of 2.2 days (mean absolute error = 3.8 days), increasing as the 
likely stay increases.  However, the day prediction is good enough to stratify risk effectively, with short stayers of 
varying severity distributed across the risk categories.

## Training the models
Please note all bash commands listed below assume the working directory is `training` (this directory).

It is also required that in this current version there is a field in the training data called `IS_MAJOR` which contains a number of values of `"Y"` or `"N"`. This is because the current training process filters for ``IS_MAJOR == "Y"`.

### Install Dependencies
Ensure training dependencies are installed from both the top-level [`requirements.txt`](../requirements.txt) *and*
the training-specific [`requirements.txt`](./requirements.txt) in this directory:
```bash
$ pip install -r ../requirements.txt
$ pip install -r requirements.txt
```

### Input Data
The input data to the training process is as supplied by GHNHSFT; a CSV export from their BI warehouse. For 
completeness, the fields present in this CSV are shown here:

```csv
LENGTH_OF_STAY,LENGTH_OF_STAY_IN_MINUTES,ADMISSION_METHOD_HOSPITAL_PROVIDER_SPELL_DESCRIPTION,AGE_ON_ADMISSION,DISCHARGE_DATE_HOSPITAL_PROVIDER_SPELL,ETHNIC_CATEGORY_CODE_DESCRIPTION,DISCHARGE_READY_DATE,DIVISION_NAME_AT_ADMISSION,EXPECTED_DISCHARGE_DATE,EXPECTED_DISCHARGE_DATE_TIME,FIRST_REGULAR_DAY_OR_NIGHT_ADMISSION_DESCRIPTION,FIRST_START_DATE_TIME_WARD_STAY,FIRST_WARD_STAY_IDENTIFIER,IS_PATIENT_DEATH_DURING_SPELL,MAIN_SPECIALTY_CODE_AT_ADMISSION,MAIN_SPECIALTY_CODE_AT_ADMISSION_DESCRIPTION,PATIENT_CLASSIFICATION,PATIENT_CLASSIFICATION_DESCRIPTION,POST_CODE_AT_ADMISSION_DATE_DISTRICT,SOURCE_OF_ADMISSION_HOSPITAL_PROVIDER_SPELL,SOURCE_OF_ADMISSION_HOSPITAL_PROVIDER_SPELL_DESCRIPTION,START_DATE_HOSPITAL_PROVIDER_SPELL,START_DATE_TIME_HOSPITAL_PROVIDER_SPELL,TREATMENT_FUNCTION_CODE_AT_ADMISSION,TREATMENT_FUNCTION_CODE_AT_ADMISSION_DESCRIPTION,elective_or_non_elective,stroke_ward_stay,PATIENT_GENDER_CURRENT,PATIENT_GENDER_CURRENT_DESCRIPTION,LOCAL_PATIENT_IDENTIFIER,SpellDominantProcedure,all_diagnoses,cds_unique_identifier,previous_30_day_hospital_provider_spell_number,ED_attendance_episode_number,unique_internal_ED_admission_number,unique_internal_IP_admission_number,reason_for_admission,IS_care_home_on_admission,IS_care_home_on_discharge,ae_attendance_category,ae_arrival_mode,ae_attendance_disposal,ae_attendance_category_code,healthcare_resource_group_code,presenting_complaint_code,presenting_complaint,wait,wait_minutes,all_investigation_codes,all_diagnosis_codes,all_treatment_codes,all_breach_reason_codes,all_location_codes,all_investigations,all_diagnosis,all_treatments,all_local_investigation_codes,all_local_investigations,all_local_treatment_codes,all_local_treatments,attendance_type,initial_wait,initial_wait_minutes,major_minor,IS_major,ae_patient_group_code,ae_patient_group,ae_initial_assessment_triage_category_code,ae_initial_assessment_triage_category,manchester_triage_category,arrival_day_of_week,arrival_month_name,Illness Injury Flag,Mental Health Flag,Frailty Proxy,Presenting Complaint Group,IS_cancer,cancer_type,IS_chronic_kidney_disease,IS_COPD,IS_coronary_heart_disease,IS_dementia,IS_diabetes,diabetes_type,IS_frailty_proxy,IS_hypertension,IS_mental_health,IMD county decile,District,Rural urban classification,OAC Group Name,OAC Subgroup Name,OAC Supergroup Name,EMCountLast12m,EL CountLast12m,ED CountLast12m,OP First CountLast12m,OP FU CountLast12m
```

No additional data preparation is required before beginning training: this raw CSV is parsed, vectorised, filtered, and
segmented for train/test by the common [`DataHandler`](loader.py) class.

### LoS Predictor
 - [Training source](train_los.py)
 - [Model source](../ltss/los_model.py)

There are a number of parameters to the training script, available using the `--help` flag:
```
$ python3 train_los.py --help
usage: train_los.py [-h] --data DATA [--checkpoint CHECKPOINT] [--cpu] [--epochs EPOCHS] [--batches-per-epoch BATCHES_PER_EPOCH] [--batch-size BATCH_SIZE] [--validation-size VALIDATION_SIZE] [--shuffle-data]
                    [--shuffle-seed SHUFFLE_SEED] [--max-samples MAX_SAMPLES] [--save-frequency SAVE_FREQUENCY]

Train DC-GAN Discriminator model

optional arguments:
  -h, --help            show this help message and exit
  --data DATA, -d DATA  Input CSV data file
  --checkpoint CHECKPOINT, -c CHECKPOINT
                        Optional checkpoint file to resume from
  --cpu                 Disable CUDA, running all training on the CPU
  --epochs EPOCHS, -e EPOCHS
                        Number of epochs to run for
  --batches-per-epoch BATCHES_PER_EPOCH, -b BATCHES_PER_EPOCH
                        Number of batches per epoch
  --batch-size BATCH_SIZE, -s BATCH_SIZE
                        Batch size (number of samples per batch)
  --validation-size VALIDATION_SIZE, -v VALIDATION_SIZE
                        Number of validation samples to use
  --shuffle-data        Whether to shuffle data before sampling
  --shuffle-seed SHUFFLE_SEED
                        Optionally seed the PRNG for consistent shuffling
  --max-samples MAX_SAMPLES
                        Maximum number of records to use for train/test splits
  --save-frequency SAVE_FREQUENCY
                        Save a model checkpoint every N epochs
```

To replicate the reported results, the model was trained using the following command:

```bash
$ python3 train_los.py -d '/path/to/NHSX Polygeist data 1617 to 2021 v2.csv' -e 500 --shuffle-data --shuffle-seed 100 --save-frequency 10
```

#### Checking and Validation
You can monitor the LoS model training using `tensorboard --logdir=./runs`. This will show live statistics of the 
mean absolute error on the current training and validation cut, as well as the limits of agreement on the validation 
data. Once the model has finished training, identify the optimal epoch and the related model checkpoint will be 
named `mod_ep_<epoch>`.

### LTSS Risk Stratification
 - [Training source](train_risk.py)
 - [Model source](../ltss/risk_model.py)

The risk stratification model uses the training cut of the data to create cumulative density functions describing the
likelihood of a particular LoS, given a particular univariate factor. It combines the CDFs for each of the categories 
and assumes they have equal weighting; as the number of categories increases, the CDF trends toward the mean CDF.

This then allows a number of days / risk category to be produced based on the CDFs with a given confidence. By fixing
the confidence value, for example at 95%, we can predict with a fixed (e.g., 5%) error what the likely maximum
stay is.

As with the LoS model, there are tunable parameters to the training:
```
$ python3 train_risk.py -h
usage: train_risk.py [-h] --data DATA --save-path SAVE_PATH [--shuffle-data] [--shuffle-seed SHUFFLE_SEED] [--max-samples MAX_SAMPLES] [--plot-distributions]

Train CDFM Risk Scoring Model

optional arguments:
  -h, --help            show this help message and exit
  --data DATA, -d DATA  Input CSV data file
  --save-path SAVE_PATH, -s SAVE_PATH
                        Path to save trained model data to
  --shuffle-data        Whether to shuffle data before sampling
  --shuffle-seed SHUFFLE_SEED
                        Optionally seed the PRNG for consistent shuffling
  --max-samples MAX_SAMPLES
                        Maximum number of records to use for train/test splits
  --plot-distributions  Plot distribution summaries
```

The results in the report can be replicated by training with the following command:

```bash
$ python3 train_risk.py -d '/path/to/NHSX Polygeist data 1617 to 2021 v2.csv' -s risk_model.pickle --shuffle-data --shuffle-seed 100
```

# Training model and creating the files needed to test the repo

Here are the step by step commands to run in bash to generate the fake data and model files needed to test the repo setup. This should be run once all dependencies have been installed. (Please see the `Install Dependencies` section above).

Please note all bash commands listed below assume the starting working directory is `training` (this directory):
```
skunkworks-long-stayer-risk-stratification\training
```

Please see [fake data generation README](../fake_data_generation\README.md#Overview-and-Purpose) to to read the intended purpose and usage of the fake data.

## 1. Generate `fake_training_data.csv`
This is to generate the fake training data.

Run the following command in the terminal ensuring the terminal is in `training` directory.

  ```bash
  $ python3 ../fake_data_generation/generate_fake_data.py -nr 200 -fn "fake_training_data" --only_major_cases
  ```
  Once successfully run the following message will appear in the terminal:

  ```
  fake data Generated! File saved: fake_training_data.csv with 200 records created. Seed was set to None.
  ```
  You should now see a file called `fake_training_data.csv` in this directory (`training`).

## 2. Generate `fake_example_records.csv`
This to generate some fake example records.

Run the following command in the terminal ensuring the terminal is in `training` directory.

 ```bash
  $ python3 ../fake_data_generation/generate_fake_data.py -nr 20 -fn "fake_example_records" --only_major_cases
```

Once successfully run the following message will appear in the terminal:

```
fake data Generated! File saved: fake_example_records.csv with 20 records created. Seed was set to None.
```
You should now see a file called `fake_example_records.csv` in this directory (`training`).

## 3. Running the LoS Predictor
This to run the LoS Model

Once the fake data has been generated, run the following command (remaining in the same directory: `training`).

```
$ python3 train_los.py -d 'fake_training_data.csv' -e 2 --shuffle-data --shuffle-seed 10 --save-frequency 1
```

Note the data the model with this command is not being trained to optimise performance for prediction. The settings in the command above are so the training is completed faster to generate a file that can be used to test the set up.

## 4. Saving the LoS model as `.state`
This is to save the trained LoS model.

In the `training` you should now see three files `mod_ep_0`, `mod_ep_1`, `mod_ep_2`. For the purposes of just converting a file to test the set up of the repo, `mod_ep_2` will be renamed to `los_model.state` .

```
$ mv mod_ep_2 los_model.state
```
A file called `los_model.state` should now appear in the `training` directory.

### 5. Running the risk model
This is to run the risk model.

Run the following command (remaining in the same directory: `training`).

```bash
$ python3 train_risk.py -d 'fake_training_data.csv' -s risk_model.pickle --shuffle-data --shuffle-seed 100
```
A file called `risk_model.pickle` should now appear in the `training` directory.

All the files have now been generated to test the set up. Instructions on deploy can be [found here](../Deploy/README.md).